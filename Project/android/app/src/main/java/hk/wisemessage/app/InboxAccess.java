package hk.wisemessage.app;

import android.content.Context;
import android.database.Cursor;
import android.provider.Telephony;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/** Read-only access to Android's inbox. Bulk import survives activity/navigation recreation. */
final class InboxAccess {
    private static final ExecutorService IMPORTER = Executors.newSingleThreadExecutor();
    private static final AtomicBoolean BUSY = new AtomicBoolean();
    private static final AtomicBoolean STOP = new AtomicBoolean();
    private static volatile Progress progress = new Progress(false, false, false, 0, 0, 0);
    private static final String[] COLUMNS = {Telephony.Sms._ID, Telephony.Sms.ADDRESS,
            Telephony.Sms.BODY, Telephony.Sms.DATE};

    private InboxAccess() {}

    static long receivedToday(Context context) {
        ZoneId zone = ZoneId.systemDefault();
        LocalDate date = LocalDate.now(zone);
        long start = date.atStartOfDay(zone).toInstant().toEpochMilli();
        long end = date.plusDays(1).atStartOfDay(zone).toInstant().toEpochMilli();
        try (Cursor cursor = context.getContentResolver().query(Telephony.Sms.Inbox.CONTENT_URI,
                new String[]{Telephony.Sms._ID}, Telephony.Sms.DATE + ">=? AND " + Telephony.Sms.DATE + "<?",
                new String[]{Long.toString(start), Long.toString(end)}, null)) {
            if (cursor == null) throw new IllegalStateException("SMS provider unavailable");
            return cursor.getCount();
        }
    }

    static InboxPage readPage(Context context, Position after, int limit) {
        int pageSize = Math.max(1, Math.min(50, limit));
        String selection = after == null ? null : "(" + Telephony.Sms.DATE + "<? OR ("
                + Telephony.Sms.DATE + "=? AND " + Telephony.Sms._ID + "<?))";
        String[] arguments = after == null ? null : new String[]{Long.toString(after.received),
                Long.toString(after.received), Long.toString(after.id)};
        List<Sms> rows = new ArrayList<>();
        try (Cursor cursor = context.getContentResolver().query(Telephony.Sms.Inbox.CONTENT_URI,
                COLUMNS, selection, arguments, Telephony.Sms.DATE + " DESC, " + Telephony.Sms._ID + " DESC")) {
            if (cursor == null) throw new IllegalStateException("SMS provider unavailable");
            while (rows.size() <= pageSize && cursor.moveToNext()) rows.add(read(cursor));
        }
        boolean hasMore = rows.size() > pageSize;
        if (hasMore) rows.remove(rows.size() - 1);
        Sms last = rows.isEmpty() ? null : rows.get(rows.size() - 1);
        return new InboxPage(rows, hasMore, last == null ? null : new Position(last.received, last.id));
    }

    static boolean startFullScan(Context context) {
        if (!BUSY.compareAndSet(false, true)) return false;
        Context app = context.getApplicationContext();
        STOP.set(false);
        progress = new Progress(true, false, false, 0, 0, 0);
        IMPORTER.execute(() -> {
            int seen = 0, added = 0, existing = 0;
            boolean failed = false;
            try (Cursor cursor = app.getContentResolver().query(Telephony.Sms.Inbox.CONTENT_URI,
                    COLUMNS, null, null, Telephony.Sms.DATE + " DESC, " + Telephony.Sms._ID + " DESC")) {
                if (cursor == null) throw new IllegalStateException("SMS provider unavailable");
                MessageStore store = MessageStore.get(app);
                while (!STOP.get() && cursor.moveToNext()) {
                    Sms sms = read(cursor);
                    long id = store.enqueue(sms.sender, sms.body, sms.received, "inbox");
                    if (id < 0) {
                        MessageStore.Record record = store.findExisting(sms.sender, sms.body, sms.received);
                        if (record != null && store.retryFailed(record.id)) id = record.id;
                    }
                    seen++;
                    if (id > 0) added++; else existing++;
                    if (seen % 64 == 0) ScanScheduler.resumePending(app);
                    if (seen % 16 == 0) progress = new Progress(true, false, false, seen, added, existing);
                }
            } catch (RuntimeException error) {
                // Keep already committed records. Never log SMS bodies or provider exception details.
                failed = true;
            } finally {
                try { ScanScheduler.resumePending(app); } catch (RuntimeException error) { failed = true; }
                progress = new Progress(false, STOP.get(), failed, seen, added, existing);
                BUSY.set(false);
            }
        });
        return true;
    }

    static void stopAdding() { STOP.set(true); }
    static Progress progress() { return progress; }

    /** Pagination metadata contains no sender, message body or prediction. */
    static final class Position {
        final long received, id;
        Position(long received, long id) { this.received = received; this.id = id; }
    }

    static final class InboxPage {
        final List<Sms> records;
        final boolean hasMore;
        final Position next;
        InboxPage(List<Sms> records, boolean hasMore, Position next) {
            this.records = records; this.hasMore = hasMore; this.next = next;
        }
    }

    private static Sms read(Cursor cursor) {
        String sender = cursor.getString(1), body = cursor.getString(2);
        return new Sms(cursor.getLong(0), sender == null ? "" : sender,
                body == null ? "" : body, cursor.getLong(3));
    }

    static final class Sms {
        final long id, received;
        final String sender, body;
        Sms(long id, String sender, String body, long received) {
            this.id = id; this.sender = sender; this.body = body; this.received = received;
        }
    }

    static final class Progress {
        final boolean running, stopped, failed;
        final int seen, added, existing;
        Progress(boolean running, boolean stopped, boolean failed, int seen, int added, int existing) {
            this.running = running; this.stopped = stopped; this.failed = failed;
            this.seen = seen; this.added = added; this.existing = existing;
        }
    }
}
