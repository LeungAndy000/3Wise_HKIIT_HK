package hk.wisemessage.app.ml;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

/** Runs the actual JNI bridge on desktop CPU using the packaged model inputs. */
public final class NativeBridgeSmoke {
    private static int[] input(Path path) throws IOException {
        ByteBuffer buffer = ByteBuffer.wrap(Files.readAllBytes(path)).order(ByteOrder.LITTLE_ENDIAN);
        int[] values = new int[256]; buffer.asIntBuffer().get(values); return values;
    }
    public static void main(String[] args) throws Exception {
        Path model = Path.of(args[0]), export = Path.of(args[1]), out = Path.of(args[2]);
        MappedByteBuffer bytes;
        try (FileChannel channel = FileChannel.open(model, StandardOpenOption.READ)) {
            bytes = channel.map(FileChannel.MapMode.READ_ONLY, 0, channel.size());
        }
        int failuresChecked = 0;
        try { NativeMessageEngine.create(ByteBuffer.wrap(new byte[1024]), 4); throw new AssertionError("Non-direct buffer accepted"); }
        catch (IllegalArgumentException expected) { failuresChecked++; }
        try { NativeMessageEngine.create(bytes, 0); throw new AssertionError("Invalid thread count accepted"); }
        catch (IllegalArgumentException expected) { failuresChecked++; }
        long handle = NativeMessageEngine.create(bytes, 4);
        if (handle == 0) throw new AssertionError("No native handle");
        ByteBuffer result = ByteBuffer.allocate(96 * 3 * 4).order(ByteOrder.LITTLE_ENDIAN);
        int[] firstIds = null, firstMask = null, firstTypes = null;
        for (int row = 0; row < 96; row++) {
            Path input = export.resolve("binary_inputs").resolve(Integer.toString(row));
            int[] ids = input(input.resolve("input_ids.bin"));
            int[] mask = input(input.resolve("attention_mask.bin"));
            int[] types = input(input.resolve("token_type_ids.bin"));
            if (row == 0) { firstIds = ids; firstMask = mask; firstTypes = types; }
            float[] logits = NativeMessageEngine.predict(handle, ids, mask, types);
            if (logits.length != 3) throw new AssertionError("Invalid output length");
            for (float value : logits) {
                if (!Float.isFinite(value)) throw new AssertionError("Nonfinite output");
                result.putFloat(value);
            }
        }
        try { NativeMessageEngine.predict(handle, new int[3], firstMask, firstTypes); throw new AssertionError("Invalid tokens accepted"); }
        catch (IllegalArgumentException expected) { failuresChecked++; }
        NativeMessageEngine.destroy(handle);
        try { NativeMessageEngine.predict(handle, firstIds, firstMask, firstTypes); throw new AssertionError("Closed handle accepted"); }
        catch (IllegalArgumentException expected) { failuresChecked++; }
        NativeMessageEngine.destroy(handle);
        Files.write(out, result.array());
        System.out.println("{\"samples\":96,\"error_paths_checked\":" + failuresChecked + "}");
    }
}
