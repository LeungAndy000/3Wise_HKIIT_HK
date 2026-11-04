package hk.wisemessage.app;

import hk.wisemessage.app.ml.Prediction;
import org.junit.Test;
import static org.junit.Assert.*;

public final class ResultFilterTest {
    @Test public void spamAndScamAreHarmfulEvenWithoutFlags() {
        assertTrue(ResultFilter.HARMFUL.matches("complete", "spam", false, false));
        assertTrue(ResultFilter.HARMFUL.matches("complete", "scam", false, false));
        assertFalse(ResultFilter.LOW_RISK.matches("complete", "spam", false, false));
    }

    @Test public void explicitScamFlagCannotBeLowRisk() {
        assertTrue(ResultFilter.HARMFUL.matches("complete", "normal", true, false));
        assertFalse(ResultFilter.LOW_RISK.matches("complete", "normal", true, false));
        assertFalse(ResultFilter.REVIEW.matches("complete", "normal", true, false));
    }

    @Test public void normalWithCombinedUnwantedProbabilityRemainsReview() {
        // Normal is the largest individual class, but spam + scam still exceeds .5.
        Prediction p = Prediction.fromLogits(new float[]{0.2f, 0.1f, 0f}, .5, false, 1);
        assertEquals("normal", p.label);
        assertTrue(p.isUnwanted);
        assertFalse(p.isScam);
        assertTrue(ResultFilter.REVIEW.matches("complete", p.label, p.isScam, p.isUnwanted));
        assertFalse(ResultFilter.LOW_RISK.matches("complete", p.label, p.isScam, p.isUnwanted));
        assertFalse(ResultFilter.HARMFUL.matches("complete", p.label, p.isScam, p.isUnwanted));
    }

    @Test public void unflaggedCompleteNormalIsOnlyLowRisk() {
        assertTrue(ResultFilter.LOW_RISK.matches("complete", "normal", false, false));
        assertFalse(ResultFilter.HARMFUL.matches("complete", "normal", false, false));
        assertFalse(ResultFilter.REVIEW.matches("complete", "normal", false, false));
    }

    @Test public void pendingFailedAndUnexpectedLabelsNeedReview() {
        for (String state : new String[]{"pending", "failed", "unexpected"}) {
            assertTrue(ResultFilter.REVIEW.matches(state, "scam", true, true));
            assertFalse(ResultFilter.HARMFUL.matches(state, "scam", true, true));
        }
        assertTrue(ResultFilter.REVIEW.matches("complete", null, false, false));
        assertTrue(ResultFilter.REVIEW.matches("complete", "other", false, false));
    }

    @Test public void everyRecordBelongsToExactlyOneCategoryPlusAll() {
        for (String state : new String[]{"pending", "failed", "complete", "other"}) {
            for (String label : new String[]{null, "normal", "spam", "scam", "other"}) {
                for (boolean scam : new boolean[]{false, true}) {
                    for (boolean unwanted : new boolean[]{false, true}) {
                        int matched = 0;
                        for (ResultFilter filter : new ResultFilter[]{ResultFilter.HARMFUL,
                                ResultFilter.LOW_RISK, ResultFilter.REVIEW}) {
                            if (filter.matches(state, label, scam, unwanted)) matched++;
                        }
                        assertEquals(1, matched);
                        assertTrue(ResultFilter.ALL.matches(state, label, scam, unwanted));
                    }
                }
            }
        }
    }

    @Test public void missingAndInvalidFlagsNeedReviewInsteadOfReassurance() {
        for (Integer invalid : new Integer[]{null, -1, 2}) {
            assertFalse(ResultFilter.LOW_RISK.matches("complete", "normal", invalid, Integer.valueOf(0)));
            assertTrue(ResultFilter.REVIEW.matches("complete", "normal", invalid, Integer.valueOf(0)));
            assertFalse(ResultFilter.LOW_RISK.matches("complete", "normal", Integer.valueOf(0), invalid));
            assertTrue(ResultFilter.REVIEW.matches("complete", "normal", Integer.valueOf(0), invalid));
        }
    }

    @Test public void metadataValidityRequiresCompletionKnownLabelAndBinaryFlags() {
        assertTrue(ResultFilter.validDecisionMetadata("complete", "normal", 0, 0));
        assertTrue(ResultFilter.validDecisionMetadata("complete", "scam", 1, 1));
        assertFalse(ResultFilter.validDecisionMetadata("pending", "normal", 0, 0));
        assertFalse(ResultFilter.validDecisionMetadata("complete", "unexpected", 0, 0));
        assertFalse(ResultFilter.validDecisionMetadata("complete", "normal", null, 0));
        assertFalse(ResultFilter.validDecisionMetadata("complete", "normal", 0, 2));
    }
}
