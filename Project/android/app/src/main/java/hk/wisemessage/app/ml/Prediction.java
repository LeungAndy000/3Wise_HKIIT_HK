package hk.wisemessage.app.ml;

/** Class evidence and app decisions; class scores do not authenticate a sender. */
public final class Prediction {
    public final String label;
    public final double normalProbability, spamProbability, scamProbability;
    public final boolean isScam, isUnwanted, truncated;
    public final long inferenceMillis;

    private Prediction(int selected, double[] scores, double unwantedThreshold, boolean truncated, long elapsed) {
        label = new String[]{"normal", "spam", "scam"}[selected];
        normalProbability = scores[0]; spamProbability = scores[1]; scamProbability = scores[2];
        isScam = selected == 2;
        isUnwanted = scores[1] + scores[2] >= unwantedThreshold;
        this.truncated = truncated; inferenceMillis = elapsed;
    }

    public static Prediction fromLogits(float[] logits, double unwantedThreshold, boolean truncated, long elapsed) {
        if (logits == null || logits.length != 3 || !Double.isFinite(unwantedThreshold)
                || unwantedThreshold < 0 || unwantedThreshold > 1) throw new IllegalArgumentException("Invalid classifier outputs");
        int selected = 0;
        for (int i = 0; i < 3; i++) {
            if (!Float.isFinite(logits[i])) throw new IllegalArgumentException("Nonfinite classifier outputs");
            if (logits[i] > logits[selected]) selected = i;
        }
        double[] scores = new double[3]; double sum = 0;
        for (int i = 0; i < 3; i++) { scores[i] = Math.exp((double) logits[i] - logits[selected]); sum += scores[i]; }
        for (int i = 0; i < 3; i++) scores[i] /= sum;
        return new Prediction(selected, scores, unwantedThreshold, truncated, elapsed);
    }
}
