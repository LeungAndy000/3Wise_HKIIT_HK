package hk.wisemessage.app;

/**
 * Categories for browsing stored decisions, not new model decisions.
 * Low risk means the existing classifier did not flag the SMS; it does not
 * authenticate the sender or promise that the content is safe.
 */
enum ResultFilter {
    HARMFUL,
    LOW_RISK,
    REVIEW,
    ALL;

    private static final String HARMFUL_SQL = "state='complete' AND "
            + "(COALESCE(label,'') IN ('spam','scam') OR COALESCE(is_scam,0)=1)";
    private static final String LOW_RISK_SQL = "state='complete' AND COALESCE(label,'')='normal' "
            + "AND COALESCE(is_unwanted,-1)=0 AND COALESCE(is_scam,-1)=0";

    /** Trusted static SQL only; the caller must append cursor parameters separately. */
    String sqlPredicate() {
        switch (this) {
            case HARMFUL: return "(" + HARMFUL_SQL + ")";
            case LOW_RISK: return "(" + LOW_RISK_SQL + ")";
            case REVIEW: return "NOT ((" + HARMFUL_SQL + ") OR (" + LOW_RISK_SQL + "))";
            case ALL: return "1=1";
            default: throw new AssertionError(this);
        }
    }

    /** Same policy for pure unit tests and record-level callers. */
    boolean matches(String state, String label, boolean isScam, boolean isUnwanted) {
        return matches(state, label, Integer.valueOf(isScam ? 1 : 0), Integer.valueOf(isUnwanted ? 1 : 0));
    }

    /** Missing or non-binary persisted flags cannot establish a low-risk result. */
    boolean matches(String state, String label, Integer scamFlag, Integer unwantedFlag) {
        boolean complete = "complete".equals(state);
        boolean isScam = Integer.valueOf(1).equals(scamFlag);
        boolean harmful = complete && ("spam".equals(label) || "scam".equals(label) || isScam);
        boolean lowRisk = complete && "normal".equals(label)
                && Integer.valueOf(0).equals(scamFlag) && Integer.valueOf(0).equals(unwantedFlag);
        switch (this) {
            case HARMFUL: return harmful;
            case LOW_RISK: return lowRisk;
            case REVIEW: return !harmful && !lowRisk;
            case ALL: return true;
            default: throw new AssertionError(this);
        }
    }

    static boolean validDecisionMetadata(String state, String label, Integer scamFlag, Integer unwantedFlag) {
        boolean knownLabel = "normal".equals(label) || "spam".equals(label) || "scam".equals(label);
        return "complete".equals(state) && knownLabel && binaryFlag(scamFlag) && binaryFlag(unwantedFlag);
    }

    private static boolean binaryFlag(Integer flag) {
        return Integer.valueOf(0).equals(flag) || Integer.valueOf(1).equals(flag);
    }
}
