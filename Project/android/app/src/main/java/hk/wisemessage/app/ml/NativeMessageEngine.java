package hk.wisemessage.app.ml;

import java.io.IOException;
import java.nio.ByteBuffer;

/** Narrow JNI bridge to the bundled MindSpore Lite CPU runtime. */
public final class NativeMessageEngine {
    static { System.loadLibrary("wisemessage_native"); }
    private NativeMessageEngine() {}
    public static native long create(ByteBuffer modelBytes, int threads) throws IOException;
    public static native float[] predict(long handle, int[] inputIds, int[] attentionMask, int[] tokenTypeIds) throws IOException;
    public static native void destroy(long handle);
}
