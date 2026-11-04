import hk.wisemessage.app.ml.WordPieceTokenizer;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Desktop JVM check of the exact tokenizer source shipped in the Android app. */
public final class TokenizerProbe {
    public static void main(String[] args) throws Exception {
        WordPieceTokenizer tokenizer = new WordPieceTokenizer(Files.newBufferedReader(Path.of(args[0]), StandardCharsets.UTF_8), 256);
        try (BufferedReader input = Files.newBufferedReader(Path.of(args[1]), StandardCharsets.UTF_8)) {
            String line;
            while ((line = input.readLine()) != null) {
                String text = new String(Base64.getDecoder().decode(line), StandardCharsets.UTF_8);
                WordPieceTokenizer.Encoding value = tokenizer.encode(text);
                System.out.println("{\"input_ids\":" + Arrays.toString(value.inputIds)
                        + ",\"attention_mask\":" + Arrays.toString(value.attentionMask)
                        + ",\"token_type_ids\":" + Arrays.toString(value.tokenTypeIds)
                        + ",\"truncated\":" + value.truncated + "}");
            }
        }
    }
}
