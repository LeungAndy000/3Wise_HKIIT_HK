package hk.wisemessage.app;

import android.Manifest;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.provider.Telephony;
import android.telephony.SmsMessage;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Fast receiver: reconstruct multipart SMS, persist it, then hand inference to JobScheduler. */
public final class SmsReceiver extends BroadcastReceiver {
    private static final ExecutorService RECEIVER_IO = Executors.newSingleThreadExecutor();
    @Override public void onReceive(Context context, Intent intent) {
        if (!Telephony.Sms.Intents.SMS_RECEIVED_ACTION.equals(intent.getAction())
                || !AppPreferences.monitoring(context)
                || context.checkSelfPermission(Manifest.permission.RECEIVE_SMS) != PackageManager.PERMISSION_GRANTED) return;
        SmsMessage[] parts;
        try { parts = Telephony.Sms.Intents.getMessagesFromIntent(intent); }
        catch (RuntimeException e) { return; }
        if (parts == null || parts.length == 0) return;
        // A standard multipart broadcast contains one sender. Group defensively if it does not.
        Map<String, IncomingMessage> messages = new LinkedHashMap<>();
        for (SmsMessage part : parts) {
            if (part == null || part.getMessageBody() == null) continue;
            String sender = part.getOriginatingAddress() == null ? "" : part.getOriginatingAddress();
            IncomingMessage message = messages.get(sender);
            if (message == null) {
                message = new IncomingMessage(sender, part.getTimestampMillis()); messages.put(sender, message);
            }
            message.body.append(part.getMessageBody());
        }
        if (messages.isEmpty()) return;
        PendingResult pendingResult = goAsync();
        Context application = context.getApplicationContext();
        RECEIVER_IO.execute(() -> {
            try {
                if (!AppPreferences.monitoring(application)) return;
                for (IncomingMessage message : messages.values()) {
                    long id = MessageStore.get(application).enqueue(message.sender, message.body.toString(), message.timestamp, "incoming");
                    if (id > 0) ScanScheduler.schedule(application, id);
                }
            } catch (RuntimeException ignored) {
                // Never log message bodies or interfere with delivery to the user's messaging app.
            } finally { pendingResult.finish(); }
        });
    }
    private static final class IncomingMessage {
        final String sender; final long timestamp; final StringBuilder body = new StringBuilder();
        IncomingMessage(String sender, long timestamp) { this.sender=sender; this.timestamp=timestamp; }
    }
}
