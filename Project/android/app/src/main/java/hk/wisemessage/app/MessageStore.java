package hk.wisemessage.app;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.TimeZone;
import hk.wisemessage.app.ml.Prediction;

/** App-private SMS records. Never changes the system SMS provider. No text is logged. */
final class MessageStore extends SQLiteOpenHelper {
    private static MessageStore instance;
    static synchronized MessageStore get(Context context) {
        if (instance == null) instance = new MessageStore(context.getApplicationContext());
        return instance;
    }
    private MessageStore(Context context) { super(context, "wisemessage_private.db", null, 2); }
    @Override public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE messages (_id INTEGER PRIMARY KEY AUTOINCREMENT, fingerprint TEXT UNIQUE NOT NULL, "
                + "sender TEXT NOT NULL, body TEXT NOT NULL, received INTEGER NOT NULL, source TEXT NOT NULL, "
                + "state TEXT NOT NULL DEFAULT 'pending', label TEXT, normal REAL, spam REAL, scam REAL, "
                + "is_scam INTEGER, is_unwanted INTEGER, truncated INTEGER, inference_ms INTEGER, completed_at INTEGER)");
        db.execSQL("CREATE INDEX pending_messages ON messages(state, _id)");
        createStatisticsIndexes(db);
    }
    @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        if (newVersion > 2) {
            throw new IllegalStateException("A newer database requires an explicit non-destructive migration");
        }
        if (oldVersion < 2) {
            // Existing predictions stay intact. Their original completion date was never stored,
            // so leave it unknown instead of attributing old checks to today or their SMS date.
            db.execSQL("ALTER TABLE messages ADD COLUMN completed_at INTEGER");
            createStatisticsIndexes(db);
        }
    }
    private static void createStatisticsIndexes(SQLiteDatabase db) {
        db.execSQL("CREATE INDEX IF NOT EXISTS received_messages ON messages(received)");
        db.execSQL("CREATE INDEX IF NOT EXISTS completed_messages ON messages(completed_at)");
    }
    long enqueue(String sender, String body, long received, String source) {
        if (body == null || body.trim().isEmpty()) return -1;
        ContentValues values = new ContentValues();
        String safeSender = sender == null ? "" : sender;
        values.put("fingerprint", fingerprint(safeSender, body, received));
        values.put("sender", safeSender);
        // Preserve the complete received message; the model itself reports token truncation.
        values.put("body", body);
        values.put("received", received);
        values.put("source", source);
        return getWritableDatabase().insertWithOnConflict("messages", null, values, SQLiteDatabase.CONFLICT_IGNORE);
    }
    boolean complete(long id, Prediction prediction) {
        ContentValues values = new ContentValues();
        values.put("state", "complete");
        values.put("label", prediction.label);
        values.put("normal", prediction.normalProbability);
        values.put("spam", prediction.spamProbability);
        values.put("scam", prediction.scamProbability);
        values.put("is_scam", prediction.isScam ? 1 : 0);
        values.put("is_unwanted", prediction.isUnwanted ? 1 : 0);
        values.put("truncated", prediction.truncated ? 1 : 0);
        values.put("inference_ms", prediction.inferenceMillis);
        values.put("completed_at", System.currentTimeMillis());
        return getWritableDatabase().update("messages", values, "_id=? AND state='pending'", new String[]{Long.toString(id)}) == 1;
    }
    void fail(long id) {
        ContentValues values = new ContentValues(); values.put("state", "failed");
        getWritableDatabase().update("messages", values, "_id=? AND state='pending'", new String[]{Long.toString(id)});
    }
    /** Explicit user retry: reuse the same private record and leave completed results untouched. */
    boolean retryFailed(long id) {
        ContentValues values = new ContentValues(); values.put("state", "pending");
        return getWritableDatabase().update("messages", values, "_id=? AND state='failed'",
                new String[]{Long.toString(id)}) == 1;
    }
    Record find(long id) {
        try (Cursor cursor = getReadableDatabase().query("messages", null, "_id=?", new String[]{Long.toString(id)}, null, null, null)) {
            return cursor.moveToFirst() ? read(cursor) : null;
        }
    }
    Record findExisting(String sender, String body, long received) {
        if (body == null || body.trim().isEmpty()) return null;
        String hash = fingerprint(sender == null ? "" : sender, body, received);
        try (Cursor c = getReadableDatabase().query("messages", null, "fingerprint=?", new String[]{hash}, null, null, null)) {
            return c.moveToFirst() ? read(c) : null;
        }
    }
    List<Record> recent(int count) { return query(null, "received DESC, _id DESC", count); }
    List<Record> pending(int count) { return query("state='pending'", "_id ASC", count); }

    /**
     * Bounded result browsing, newest private record first. Filtering happens in
     * SQLite before LIMIT so an older harmful SMS cannot disappear behind newer
     * normal records. A positive beforeId is an exclusive keyset cursor; pass 0
     * for the first page. Call on a worker thread.
     */
    ResultPage results(ResultFilter filter, long beforeId, int pageSize) {
        if (filter == null) throw new IllegalArgumentException("A result filter is required");
        int boundedSize = Math.max(1, Math.min(25, pageSize));
        SQLiteDatabase db = getReadableDatabase();
        List<Record> records = new ArrayList<>(boundedSize);
        ResultCounts counts;
        boolean hasMore = false;
        // One short snapshot keeps the counts and rows consistent while the
        // background inference worker can complete other records between pages.
        db.beginTransactionNonExclusive();
        try {
            counts = resultCounts(db);
            String where = filter.sqlPredicate();
            String[] args = null;
            if (beforeId > 0) {
                where = "(" + where + ") AND _id<?";
                args = new String[]{Long.toString(beforeId)};
            }
            try (Cursor cursor = db.query("messages", null, where, args, null, null,
                    "_id DESC", Integer.toString(boundedSize + 1))) {
                while (cursor.moveToNext()) {
                    if (records.size() == boundedSize) { hasMore = true; break; }
                    records.add(read(cursor));
                }
            }
            db.setTransactionSuccessful();
        } finally {
            db.endTransaction();
        }
        long nextBeforeId = records.isEmpty() ? 0 : records.get(records.size() - 1).id;
        return new ResultPage(records, hasMore, nextBeforeId, counts.count(filter), counts);
    }

    private static ResultCounts resultCounts(SQLiteDatabase db) {
        String harmful = ResultFilter.HARMFUL.sqlPredicate();
        String lowRisk = ResultFilter.LOW_RISK.sqlPredicate();
        try (Cursor c = db.rawQuery("SELECT COUNT(*), "
                + "COALESCE(SUM(CASE WHEN " + harmful + " THEN 1 ELSE 0 END),0), "
                + "COALESCE(SUM(CASE WHEN " + lowRisk + " THEN 1 ELSE 0 END),0) FROM messages", null)) {
            if (!c.moveToFirst()) return new ResultCounts(0, 0, 0, 0);
            long all = c.getLong(0), harmfulCount = c.getLong(1), lowRiskCount = c.getLong(2);
            return new ResultCounts(harmfulCount, lowRiskCount, all - harmfulCount - lowRiskCount, all);
        }
    }

    /**
     * App-private history only. received excludes manual entries; checked includes manual checks.
     * The system inbox must be queried separately to display all phone arrivals, including SMS
     * received while monitoring was off. Call on a worker, not the UI thread.
     */
    Statistics statistics() { return statistics(System.currentTimeMillis(), TimeZone.getDefault()); }

    Statistics statistics(long nowMillis, TimeZone timeZone) {
        SQLiteDatabase db = getReadableDatabase();
        long[] totals = new long[9];
        try (Cursor c = db.rawQuery("SELECT "
                + "COALESCE(SUM(CASE WHEN source IN ('incoming','inbox') THEN 1 ELSE 0 END),0), "
                + "COALESCE(SUM(CASE WHEN state='complete' THEN 1 ELSE 0 END),0), "
                + "COALESCE(SUM(CASE WHEN state='complete' AND label='scam' THEN 1 ELSE 0 END),0), "
                + "COALESCE(SUM(CASE WHEN state='complete' AND label='spam' THEN 1 ELSE 0 END),0), "
                + "COALESCE(SUM(CASE WHEN state='complete' AND label='normal' AND COALESCE(is_unwanted,0)=0 THEN 1 ELSE 0 END),0), "
                + "COALESCE(SUM(CASE WHEN state='pending' THEN 1 ELSE 0 END),0), "
                + "COALESCE(SUM(CASE WHEN state='failed' THEN 1 ELSE 0 END),0), "
                + "COALESCE(SUM(CASE WHEN state='complete' AND completed_at IS NULL THEN 1 ELSE 0 END),0), "
                + "COALESCE(SUM(CASE WHEN state='complete' AND label='normal' AND is_unwanted=1 THEN 1 ELSE 0 END),0) "
                + "FROM messages", null)) {
            if (c.moveToFirst()) for (int i=0; i<totals.length; i++) totals[i]=c.getLong(i);
        }
        List<DayStatistics> days = new ArrayList<>(7);
        for (int offset = -6; offset <= 0; offset++) {
            StatisticsWindow day = StatisticsWindow.day(nowMillis, timeZone, offset);
            String[] bounds = {Long.toString(day.startMillis), Long.toString(day.endMillis)};
            long received;
            try (Cursor c = db.rawQuery("SELECT COUNT(*) FROM messages WHERE source IN ('incoming','inbox') "
                    + "AND received>=? AND received<?", bounds)) {
                received = c.moveToFirst() ? c.getLong(0) : 0;
            }
            try (Cursor c = db.rawQuery("SELECT COUNT(*), "
                    + "COALESCE(SUM(CASE WHEN label='scam' THEN 1 ELSE 0 END),0), "
                    + "COALESCE(SUM(CASE WHEN label='spam' THEN 1 ELSE 0 END),0), "
                    + "COALESCE(SUM(CASE WHEN label='normal' AND COALESCE(is_unwanted,0)=0 THEN 1 ELSE 0 END),0), "
                    + "COALESCE(SUM(CASE WHEN label='normal' AND is_unwanted=1 THEN 1 ELSE 0 END),0) "
                    + "FROM messages WHERE state='complete' AND completed_at>=? AND completed_at<?", bounds)) {
                if (c.moveToFirst()) days.add(new DayStatistics(day.startMillis, day.endMillis, received,
                        c.getLong(0), c.getLong(1), c.getLong(2), c.getLong(3), c.getLong(4)));
                else days.add(new DayStatistics(day.startMillis, day.endMillis, received, 0, 0, 0, 0, 0));
            }
        }
        return new Statistics(totals[0], totals[1], totals[2], totals[3], totals[4], totals[5], totals[6], totals[7], totals[8], days);
    }
    private List<Record> query(String where, String order, int limit) {
        List<Record> records = new ArrayList<>();
        try (Cursor cursor = getReadableDatabase().query("messages", null, where, null, null, null, order, Integer.toString(limit))) {
            while (cursor.moveToNext()) records.add(read(cursor));
        }
        return records;
    }
    private static Record read(Cursor c) {
        String state = c.getString(c.getColumnIndexOrThrow("state"));
        String label = c.getString(c.getColumnIndexOrThrow("label"));
        int scamIndex = c.getColumnIndexOrThrow("is_scam"), unwantedIndex = c.getColumnIndexOrThrow("is_unwanted");
        Integer scamFlag = c.isNull(scamIndex) ? null : c.getInt(scamIndex);
        Integer unwantedFlag = c.isNull(unwantedIndex) ? null : c.getInt(unwantedIndex);
        return new Record(c.getLong(c.getColumnIndexOrThrow("_id")), c.getString(c.getColumnIndexOrThrow("sender")),
                c.getString(c.getColumnIndexOrThrow("body")), c.getLong(c.getColumnIndexOrThrow("received")),
                c.getString(c.getColumnIndexOrThrow("source")), state,
                label, c.getDouble(c.getColumnIndexOrThrow("normal")),
                c.getDouble(c.getColumnIndexOrThrow("spam")), c.getDouble(c.getColumnIndexOrThrow("scam")),
                c.getInt(c.getColumnIndexOrThrow("is_scam")) == 1, c.getInt(c.getColumnIndexOrThrow("is_unwanted")) == 1,
                c.getInt(c.getColumnIndexOrThrow("truncated")) == 1, c.getLong(c.getColumnIndexOrThrow("inference_ms")),
                c.isNull(c.getColumnIndexOrThrow("completed_at")) ? 0 : c.getLong(c.getColumnIndexOrThrow("completed_at")),
                ResultFilter.validDecisionMetadata(state, label, scamFlag, unwantedFlag));
    }
    private static String fingerprint(String sender, String body, long time) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest((sender + '\0' + time + '\0' + body).getBytes(StandardCharsets.UTF_8));
            StringBuilder out = new StringBuilder(64);
            for (byte b : digest) out.append(String.format(java.util.Locale.ROOT, "%02x", b & 255));
            return out.toString();
        } catch (java.security.NoSuchAlgorithmException e) { throw new IllegalStateException(e); }
    }
    static final class Record {
        final long id, received, inferenceMillis, completedAt;
        final String sender, body, source, state, label;
        final double normal, spam, scam;
        final boolean isScam, isUnwanted, truncated, decisionMetadataValid;
        Record(long id, String sender, String body, long received, String source, String state, String label,
                double normal, double spam, double scam, boolean isScam, boolean isUnwanted, boolean truncated, long inferenceMillis,
                long completedAt, boolean decisionMetadataValid) {
            this.id=id; this.sender=sender; this.body=body; this.received=received; this.source=source;
            this.state=state; this.label=label; this.normal=normal; this.spam=spam; this.scam=scam;
            this.isScam=isScam; this.isUnwanted=isUnwanted; this.truncated=truncated; this.inferenceMillis=inferenceMillis;
            this.completedAt=completedAt;
            this.decisionMetadataValid=decisionMetadataValid;
        }
    }

    static final class ResultPage {
        final List<Record> records;
        final boolean hasMore;
        final long nextBeforeId, totalMatched;
        final ResultCounts counts;
        ResultPage(List<Record> records, boolean hasMore, long nextBeforeId,
                long totalMatched, ResultCounts counts) {
            this.records = Collections.unmodifiableList(new ArrayList<>(records));
            this.hasMore = hasMore; this.nextBeforeId = nextBeforeId;
            this.totalMatched = totalMatched; this.counts = counts;
        }
    }

    static final class ResultCounts {
        final long harmful, lowRisk, review, all;
        ResultCounts(long harmful, long lowRisk, long review, long all) {
            this.harmful = harmful; this.lowRisk = lowRisk; this.review = review; this.all = all;
        }
        long count(ResultFilter filter) {
            switch (filter) {
                case HARMFUL: return harmful;
                case LOW_RISK: return lowRisk;
                case REVIEW: return review;
                case ALL: return all;
                default: throw new AssertionError(filter);
            }
        }
    }

    static final class DayStatistics {
        final long startMillis, endMillis, received, checked, scam, spam, normal, review;
        DayStatistics(long startMillis, long endMillis, long received, long checked, long scam, long spam, long normal, long review) {
            this.startMillis=startMillis; this.endMillis=endMillis; this.received=received; this.checked=checked;
            this.scam=scam; this.spam=spam; this.normal=normal; this.review=review;
        }
    }

    static final class Statistics {
        final long todayReceived, todayChecked, todayScam, todaySpam, todayNormal, todayReview;
        final long totalReceived, totalChecked, totalScam, totalSpam, totalNormal, totalReview, pending, failed, legacyChecked;
        final List<DayStatistics> last7Days;
        Statistics(long totalReceived, long totalChecked, long totalScam, long totalSpam, long totalNormal,
                long pending, long failed, long legacyChecked, long totalReview, List<DayStatistics> days) {
            this.totalReceived=totalReceived; this.totalChecked=totalChecked; this.totalScam=totalScam;
            this.totalSpam=totalSpam; this.totalNormal=totalNormal; this.totalReview=totalReview; this.pending=pending; this.failed=failed;
            this.legacyChecked=legacyChecked; this.last7Days=Collections.unmodifiableList(new ArrayList<>(days));
            DayStatistics today=days.get(days.size()-1);
            this.todayReceived=today.received; this.todayChecked=today.checked; this.todayScam=today.scam;
            this.todaySpam=today.spam; this.todayNormal=today.normal; this.todayReview=today.review;
        }
    }
}
