package hk.wisemessage.app;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;

final class ScamNotifications {
    static final String CHANNEL = "scam_warnings_v1";
    private ScamNotifications() {}
    static void ensureChannel(Context context) {
        context = AppLocale.wrap(context);
        NotificationManager manager = context.getSystemService(NotificationManager.class);
        if (manager == null) return;
        NotificationChannel channel = new NotificationChannel(CHANNEL, context.getString(R.string.notification_channel), NotificationManager.IMPORTANCE_HIGH);
        channel.setDescription(context.getString(R.string.notification_channel_description));
        channel.setLockscreenVisibility(Notification.VISIBILITY_PRIVATE);
        channel.enableVibration(true);
        manager.createNotificationChannel(channel);
    }
    static boolean allowed(Context context) {
        return AppPreferences.notificationsEnabled(context) && systemAllowed(context);
    }
    /** System permission state, independent of the user's in-app notification toggle. */
    static boolean systemAllowed(Context context) {
        if (Build.VERSION.SDK_INT >= 33 && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) return false;
        NotificationManager manager = context.getSystemService(NotificationManager.class);
        if (manager == null || !manager.areNotificationsEnabled()) return false;
        NotificationChannel channel = manager.getNotificationChannel(CHANNEL);
        return channel == null || channel.getImportance() != NotificationManager.IMPORTANCE_NONE;
    }
    static void showScam(Context context, long recordId) { show(context, recordId, false); }
    static boolean showTest(Context context) { return show(context, -1, true); }
    private static boolean show(Context context, long recordId, boolean test) {
        context = AppLocale.wrap(context);
        ensureChannel(context);
        if (!allowed(context)) return false;
        Intent open = new Intent(context, MainActivity.class).setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        if (recordId > 0) open.putExtra("record_id", recordId);
        int notificationId = test ? 700 : (int) (recordId % 1_000_000_000L) + 1000;
        PendingIntent tap = PendingIntent.getActivity(context, notificationId, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification publicVersion = new Notification.Builder(context, CHANNEL)
                .setSmallIcon(R.drawable.ic_notification_warning).setContentTitle(context.getString(R.string.app_name))
                .setContentText(context.getString(R.string.notification_public)).build();
        Notification notification = new Notification.Builder(context, CHANNEL)
                .setSmallIcon(R.drawable.ic_notification_warning)
                .setContentTitle(context.getString(test ? R.string.test_notification_title : R.string.notification_title))
                .setContentText(context.getString(test ? R.string.test_notification_body : R.string.notification_body))
                .setCategory(Notification.CATEGORY_STATUS).setVisibility(Notification.VISIBILITY_PRIVATE)
                .setPublicVersion(publicVersion).setContentIntent(tap).setAutoCancel(true)
                .setOnlyAlertOnce(true).setShowWhen(true).build();
        try { context.getSystemService(NotificationManager.class).notify(notificationId, notification); return true; }
        catch (SecurityException ignored) { return false; }
    }
}
