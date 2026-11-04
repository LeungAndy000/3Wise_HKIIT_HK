package hk.wisemessage.app.ml;

import org.junit.Test;
import static org.junit.Assert.*;

public final class PredictionTest {
    @Test public void scamArgmaxWarnsEvenBelowHalfProbability() {
        Prediction value = Prediction.fromLogits(new float[]{0, 0, .1f}, .5, false, 1);
        assertEquals("scam", value.label);
        assertTrue(value.isScam);
        assertTrue(value.scamProbability < .5);
    }
    @Test public void advertisingSpamIsNotMisrepresentedAsScam() {
        Prediction value = Prediction.fromLogits(new float[]{-2, 5, -1}, .5, false, 1);
        assertEquals("spam", value.label);
        assertTrue(value.isUnwanted);
        assertFalse(value.isScam);
    }
    @Test public void unknownUnwantedSubtypeKeepsItsEvidence() {
        Prediction value = Prediction.fromLogits(new float[]{(float)Math.log(.4), (float)Math.log(.3), (float)Math.log(.3)}, .5, true, 7);
        assertEquals("normal", value.label);
        assertTrue(value.isUnwanted);
        assertFalse(value.isScam);
        assertTrue(value.truncated);
        assertEquals(7, value.inferenceMillis);
    }
    @Test public void extremeLogitsRemainFiniteAndNormalized() {
        Prediction value = Prediction.fromLogits(new float[]{-10000, -9999, 10000}, .5, false, 0);
        assertEquals(1., value.normalProbability + value.spamProbability + value.scamProbability, 1e-12);
        assertEquals(1., value.scamProbability, 0.);
    }
    @Test(expected=IllegalArgumentException.class) public void nonfiniteScoresCannotBecomeSafeResults() {
        Prediction.fromLogits(new float[]{Float.NaN, 1, 2}, .5, false, 0);
    }
    @Test(expected=IllegalArgumentException.class) public void invalidThresholdIsRejected() {
        Prediction.fromLogits(new float[]{0, 1, 2}, Double.NaN, false, 0);
    }
}
