package hk.wisemessage.app.ml;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.Reader;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Local BERT basic + greedy WordPiece tokenization, matching the training vocabulary. */
public final class WordPieceTokenizer {
    private static final Pattern SPECIAL = Pattern.compile("\\[(?:PAD|UNK|CLS|SEP|MASK)\\]");
    private final Map<String, Integer> vocabulary = new HashMap<>();
    private final int maxLength, pad, cls, sep, unk;

    public WordPieceTokenizer(Reader reader, int maxLength) throws IOException {
        if (maxLength < 2) throw new IllegalArgumentException("Invalid token limit");
        this.maxLength = maxLength;
        BufferedReader input = new BufferedReader(reader);
        String line; int index = 0;
        while ((line = input.readLine()) != null) {
            if (vocabulary.put(line, index++) != null) throw new IOException("Duplicate vocabulary entry");
        }
        pad = required("[PAD]"); cls = required("[CLS]"); sep = required("[SEP]"); unk = required("[UNK]");
        required("[MASK]");
    }

    private int required(String token) throws IOException {
        Integer value = vocabulary.get(token);
        if (value == null) throw new IOException("Missing tokenizer special token");
        return value;
    }

    public int vocabularySize() { return vocabulary.size(); }

    public Encoding encode(String text) {
        if (text == null) throw new IllegalArgumentException("Message is required");
        List<Integer> tokens = new ArrayList<>();
        Matcher matcher = SPECIAL.matcher(text); int offset = 0;
        while (matcher.find()) {
            basic(text.substring(offset, matcher.start()), tokens);
            tokens.add(vocabulary.get(matcher.group())); offset = matcher.end();
        }
        basic(text.substring(offset), tokens);
        int used = Math.min(tokens.size(), maxLength - 2);
        int[] ids = new int[maxLength], mask = new int[maxLength], types = new int[maxLength];
        java.util.Arrays.fill(ids, pad);
        ids[0] = cls; mask[0] = 1;
        for (int i = 0; i < used; i++) { ids[i + 1] = tokens.get(i); mask[i + 1] = 1; }
        ids[used + 1] = sep; mask[used + 1] = 1;
        return new Encoding(ids, mask, types, tokens.size() > used);
    }

    private void basic(String text, List<Integer> output) {
        StringBuilder cleaned = new StringBuilder();
        text.codePoints().forEach(code -> {
            int type = Character.getType(code);
            if (code == 0 || code == 0xfffd) return;
            if (code != '\t' && code != '\n' && code != '\r'
                    && (type == Character.CONTROL || type == Character.FORMAT
                    || type == Character.PRIVATE_USE || type == Character.SURROGATE)) return;
            if (whitespace(code)) cleaned.append(' ');
            else if (chinese(code)) cleaned.append(' ').appendCodePoint(code).append(' ');
            else cleaned.appendCodePoint(code);
        });
        // Rust tokenizers applies Unicode lowercase per scalar. Whole-string
        // Java lowercase additionally changes Greek final sigma by context.
        StringBuilder lowered = new StringBuilder();
        cleaned.toString().codePoints().forEach(code ->
                lowered.append(new String(Character.toChars(code)).toLowerCase(Locale.ROOT)));
        String normalized = Normalizer.normalize(lowered, Normalizer.Form.NFD);
        StringBuilder word = new StringBuilder();
        normalized.codePoints().forEach(code -> {
            if (Character.getType(code) == Character.NON_SPACING_MARK) return;
            if (whitespace(code)) { emit(word, output); }
            else if (punctuation(code)) { emit(word, output); word.appendCodePoint(code); emit(word, output); }
            else word.appendCodePoint(code);
        });
        emit(word, output);
    }

    private void emit(StringBuilder word, List<Integer> output) {
        if (word.length() == 0) return;
        String token = word.toString(); word.setLength(0);
        int[] points = token.codePoints().toArray();
        if (points.length > 100) { output.add(unk); return; }
        List<Integer> pieces = new ArrayList<>();
        int start = 0;
        while (start < points.length) {
            Integer selected = null; int end = points.length;
            while (end > start) {
                String candidate = new String(points, start, end - start);
                if (start > 0) candidate = "##" + candidate;
                selected = vocabulary.get(candidate);
                if (selected != null) break;
                end--;
            }
            if (selected == null) { output.add(unk); return; }
            pieces.add(selected); start = end;
        }
        output.addAll(pieces);
    }

    private static boolean whitespace(int code) {
        return (code >= 0x9 && code <= 0xd) || code == 0x20 || code == 0x85 || code == 0xa0
                || code == 0x1680 || (code >= 0x2000 && code <= 0x200a) || code == 0x2028
                || code == 0x2029 || code == 0x202f || code == 0x205f || code == 0x3000;
    }
    private static boolean punctuation(int code) {
        if ((code >= 33 && code <= 47) || (code >= 58 && code <= 64)
                || (code >= 91 && code <= 96) || (code >= 123 && code <= 126)) return true;
        int type = Character.getType(code);
        return type == Character.CONNECTOR_PUNCTUATION || type == Character.DASH_PUNCTUATION
                || type == Character.START_PUNCTUATION || type == Character.END_PUNCTUATION
                || type == Character.INITIAL_QUOTE_PUNCTUATION || type == Character.FINAL_QUOTE_PUNCTUATION
                || type == Character.OTHER_PUNCTUATION;
    }
    private static boolean chinese(int code) {
        return (code >= 0x4e00 && code <= 0x9fff) || (code >= 0x3400 && code <= 0x4dbf)
                || (code >= 0x20000 && code <= 0x2a6df) || (code >= 0x2a700 && code <= 0x2b73f)
                || (code >= 0x2b740 && code <= 0x2b81f) || (code >= 0x2b920 && code <= 0x2ceaf)
                || (code >= 0xf900 && code <= 0xfaff) || (code >= 0x2f800 && code <= 0x2fa1f);
    }

    public static final class Encoding {
        public final int[] inputIds, attentionMask, tokenTypeIds;
        public final boolean truncated;
        Encoding(int[] ids, int[] mask, int[] types, boolean truncated) {
            this.inputIds = ids; this.attentionMask = mask; this.tokenTypeIds = types; this.truncated = truncated;
        }
    }
}
