package hk.wisemessage.app;

import android.content.Context;

final class AppPreferences {
    private static final String NAME = "local_protection";
    private AppPreferences() {}
    static boolean monitoring(Context context) {
        return context.getSharedPreferences(NAME, Context.MODE_PRIVATE).getBoolean("monitoring", false);
    }
    static void setMonitoring(Context context, boolean enabled) {
        context.getSharedPreferences(NAME, Context.MODE_PRIVATE).edit().putBoolean("monitoring", enabled).apply();
    }
    /** App-level preference; Android notification permission/channel settings remain separate. */
    static boolean notificationsEnabled(Context context) {
        return context.getSharedPreferences(NAME, Context.MODE_PRIVATE).getBoolean("notifications_enabled", true);
    }
    static void setNotificationsEnabled(Context context, boolean enabled) {
        context.getSharedPreferences(NAME, Context.MODE_PRIVATE).edit().putBoolean("notifications_enabled", enabled).apply();
    }
    static boolean scannerFailed(Context context) {
        return context.getSharedPreferences(NAME, Context.MODE_PRIVATE).getBoolean("scanner_failed", false);
    }
    static void setScannerFailed(Context context, boolean failed) {
        context.getSharedPreferences(NAME, Context.MODE_PRIVATE).edit().putBoolean("scanner_failed", failed).apply();
    }
}
