package hk.wisemessage.app;

import android.app.job.JobParameters;
import android.app.job.JobService;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;
import hk.wisemessage.app.ml.LocalMessageClassifier;
import hk.wisemessage.app.ml.Prediction;

/** Durable background inference. Does not hold the SMS receiver open while loading the model. */
public final class MessageScanJobService extends JobService {
    private static final ExecutorService INFERENCE = Executors.newSingleThreadExecutor();
    private final Map<Integer, AtomicBoolean> stopped = new ConcurrentHashMap<>();
    @Override public boolean onStartJob(JobParameters parameters) {
        AtomicBoolean stop = new AtomicBoolean(false); stopped.put(parameters.getJobId(), stop);
        INFERENCE.execute(() -> {
            try {
                if (stop.get()) return;
                long id = parameters.getExtras().getLong("record_id", -1);
                MessageStore store = MessageStore.get(this);
                MessageStore.Record record = store.find(id);
                if (record == null || !"pending".equals(record.state)) return;
                // The tokenizer controls token length. SMS text remains private and is never logged.
                Prediction prediction = LocalMessageClassifier.getInstance(this).classify(record.body);
                AppPreferences.setScannerFailed(this, false);
                boolean newlyCompleted = store.complete(id, prediction);
                if (newlyCompleted && "incoming".equals(record.source) && prediction.isScam
                        && AppPreferences.monitoring(this)) ScamNotifications.showScam(this, id);
            } catch (Exception | LinkageError e) {
                AppPreferences.setScannerFailed(this, true);
                long id = parameters.getExtras().getLong("record_id", -1);
                try { MessageStore.get(this).fail(id); } catch (RuntimeException ignored) {}
            } finally {
                stopped.remove(parameters.getJobId(), stop);
                if (!stop.get()) {
                    // Drain records left pending if an earlier scheduling attempt hit the OS job limit.
                    try { ScanScheduler.resumePending(this); } catch (RuntimeException ignored) {}
                    jobFinished(parameters, false);
                }
            }
        });
        return true;
    }
    @Override public boolean onStopJob(JobParameters parameters) {
        AtomicBoolean stop = stopped.remove(parameters.getJobId());
        if (stop != null) stop.set(true);
        // A running native call may finish; the SQLite conditional update prevents duplicate alerts.
        return true;
    }
}
