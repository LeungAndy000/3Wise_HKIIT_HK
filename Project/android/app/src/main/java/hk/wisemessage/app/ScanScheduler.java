package hk.wisemessage.app;

import android.app.job.JobInfo;
import android.app.job.JobScheduler;
import android.content.ComponentName;
import android.content.Context;
import android.os.Build;
import android.os.PersistableBundle;

/** One durable job per record avoids replacing an already-running incoming-SMS job. */
final class ScanScheduler {
    private ScanScheduler() {}
    static boolean schedule(Context context, long recordId) {
        if (recordId <= 0 || recordId > Integer.MAX_VALUE - 1000L) return false;
        JobScheduler scheduler = context.getSystemService(JobScheduler.class);
        if (scheduler == null) return false;
        int jobId = (int) recordId + 1000;
        if (scheduler.getPendingJob(jobId) != null) return true;
        PersistableBundle extras = new PersistableBundle(); extras.putLong("record_id", recordId);
        JobInfo.Builder builder = new JobInfo.Builder(jobId, new ComponentName(context, MessageScanJobService.class))
                .setExtras(extras).setPersisted(true);
        try {
            if (Build.VERSION.SDK_INT >= 31) {
                try {
                    int expedited = scheduler.schedule(builder.setExpedited(true).build());
                    if (expedited == JobScheduler.RESULT_SUCCESS) return true;
                } catch (IllegalArgumentException | IllegalStateException ignored) {
                    // An OEM may reject expedited work; still try a normal durable job.
                }
                builder.setExpedited(false);
            }
            return scheduler.schedule(builder.build()) == JobScheduler.RESULT_SUCCESS;
        } catch (IllegalArgumentException | IllegalStateException | SecurityException e) {
            // The record stays pending and can be rescheduled when the app is opened.
            return false;
        }
    }
    static void resumePending(Context context) {
        for (MessageStore.Record record : MessageStore.get(context).pending(80)) schedule(context, record.id);
    }
}
