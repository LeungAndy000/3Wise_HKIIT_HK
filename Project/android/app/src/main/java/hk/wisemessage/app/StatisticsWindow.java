package hk.wisemessage.app;

import java.util.Calendar;
import java.util.TimeZone;

/** Local calendar-day boundaries. A daylight-saving day need not have 24 hours. */
final class StatisticsWindow {
    final long startMillis, endMillis;

    private StatisticsWindow(long startMillis, long endMillis) {
        this.startMillis = startMillis;
        this.endMillis = endMillis;
    }

    static StatisticsWindow day(long nowMillis, TimeZone timeZone, int offset) {
        Calendar calendar = Calendar.getInstance(timeZone);
        calendar.setTimeInMillis(nowMillis);
        calendar.set(Calendar.HOUR_OF_DAY, 0);
        calendar.set(Calendar.MINUTE, 0);
        calendar.set(Calendar.SECOND, 0);
        calendar.set(Calendar.MILLISECOND, 0);
        calendar.add(Calendar.DAY_OF_MONTH, offset);
        long start = calendar.getTimeInMillis();
        calendar.add(Calendar.DAY_OF_MONTH, 1);
        return new StatisticsWindow(start, calendar.getTimeInMillis());
    }

    boolean contains(long timestamp) {
        return timestamp >= startMillis && timestamp < endMillis;
    }

    static boolean isSmsSource(String source) {
        return "incoming".equals(source) || "inbox".equals(source);
    }
}
