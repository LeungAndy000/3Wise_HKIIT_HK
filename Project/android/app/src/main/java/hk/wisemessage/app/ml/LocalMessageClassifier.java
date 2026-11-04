package hk.wisemessage.app.ml;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.content.res.AssetManager;
import android.os.SystemClock;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.ByteBuffer;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import org.json.JSONArray;
import org.json.JSONObject;

/** One process-local, serialized FP32 CPU model. No network or SMS-provider access. */
public final class LocalMessageClassifier {
    private static final String ASSETS = "wisemessage/";
    private static volatile LocalMessageClassifier instance;
    private final long nativeHandle;
    // Keep mapped APK weights alive for the native model lifetime.
    private final MappedByteBuffer modelBuffer;
    private final WordPieceTokenizer tokenizer;
    private final String modelId;
    private final double unwantedThreshold;
    private final int maxLength;

    public static LocalMessageClassifier getInstance(Context context) throws Exception {
        LocalMessageClassifier result = instance;
        if (result == null) {
            synchronized (LocalMessageClassifier.class) {
                result = instance;
                if (result == null) instance = result = new LocalMessageClassifier(context.getApplicationContext());
            }
        }
        return result;
    }

    private LocalMessageClassifier(Context context) throws Exception {
        AssetManager assets = context.getAssets();
        JSONObject manifest = new JSONObject(new String(readAsset(assets, "manifest.json", 64 * 1024), StandardCharsets.UTF_8));
        if (manifest.getInt("format_version") != 1 || !"MindSpore Lite".equals(manifest.getString("runtime"))
                || !"model.ms".equals(manifest.getString("model_file"))
                || !"vocab.txt".equals(manifest.getString("vocab_file"))
                || !"int32".equals(manifest.getString("input_dtype"))
                || !"float32".equals(manifest.getString("output_dtype"))
                || !"argmax_scam".equals(manifest.getString("scam_decision"))
                || !"logits_softmax_required".equals(manifest.getString("output_semantics"))
                || !manifest.getBoolean("do_lower_case") || manifest.getBoolean("enable_fp16")) {
            throw new IOException("Unsupported local classifier manifest");
        }
        modelId = manifest.getString("model_id");
        maxLength = manifest.getInt("max_length");
        unwantedThreshold = manifest.getDouble("unwanted_threshold");
        if (modelId.isEmpty() || maxLength != 256 || !Double.isFinite(unwantedThreshold)
                || unwantedThreshold < 0 || unwantedThreshold > 1) throw new IOException("Invalid classifier configuration");
        JSONArray labels = manifest.getJSONArray("labels");
        if (labels.length() != 3 || !"normal".equals(labels.getString(0)) || !"spam".equals(labels.getString(1))
                || !"scam".equals(labels.getString(2))) throw new IOException("Invalid classifier labels");
        byte[] vocabulary = readAsset(assets, "vocab.txt", 1024 * 1024);
        verifyDigest(ByteBuffer.wrap(vocabulary), manifest.getString("vocab_sha256"));
        tokenizer = new WordPieceTokenizer(new InputStreamReader(new ByteArrayInputStream(vocabulary), StandardCharsets.UTF_8), maxLength);
        if (tokenizer.vocabularySize() != manifest.getInt("vocab_size")) throw new IOException("Vocabulary size mismatch");
        try (AssetFileDescriptor descriptor = assets.openFd(ASSETS + "model.ms");
             FileInputStream stream = new FileInputStream(descriptor.getFileDescriptor())) {
            modelBuffer = stream.getChannel().map(FileChannel.MapMode.READ_ONLY, descriptor.getStartOffset(), descriptor.getDeclaredLength());
        }
        verifyDigest(modelBuffer.asReadOnlyBuffer(), manifest.getString("model_sha256"));
        int threads = Math.max(1, Math.min(4, Runtime.getRuntime().availableProcessors()));
        nativeHandle = NativeMessageEngine.create(modelBuffer, threads);
        if (nativeHandle == 0) throw new IOException("Unable to initialize local MindSpore Lite model");
    }

    public String getModelId() { return modelId; }

    public synchronized Prediction classify(String text) throws IOException {
        if (text == null || text.trim().isEmpty() || text.length() > 20000) throw new IllegalArgumentException("Expected a nonempty SMS of at most 20000 characters");
        long started = SystemClock.elapsedRealtime();
        WordPieceTokenizer.Encoding encoded = tokenizer.encode(text);
        float[] logits = NativeMessageEngine.predict(nativeHandle, encoded.inputIds, encoded.attentionMask, encoded.tokenTypeIds);
        return Prediction.fromLogits(logits, unwantedThreshold, encoded.truncated,
                SystemClock.elapsedRealtime() - started);
    }

    private static byte[] readAsset(AssetManager assets, String name, int limit) throws IOException {
        try (InputStream stream = assets.open(ASSETS + name); ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192]; int count;
            while ((count = stream.read(buffer)) != -1) {
                if (output.size() + count > limit) throw new IOException("Model metadata exceeds expected size");
                output.write(buffer, 0, count);
            }
            return output.toByteArray();
        }
    }

    private static void verifyDigest(ByteBuffer data, String expected) throws Exception {
        if (!expected.matches("[0-9a-f]{64}")) throw new IOException("Missing model asset identity");
        MessageDigest digest = MessageDigest.getInstance("SHA-256"); digest.update(data);
        StringBuilder actual = new StringBuilder();
        for (byte value : digest.digest()) actual.append(String.format(java.util.Locale.ROOT, "%02x", value & 255));
        if (!expected.contentEquals(actual)) throw new IOException("Local model asset identity mismatch");
    }
}
