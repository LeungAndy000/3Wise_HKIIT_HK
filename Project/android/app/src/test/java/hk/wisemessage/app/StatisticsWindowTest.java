package hk.wisemessage.app;

import java.time.Instant;
import java.util.TimeZone;
import org.junit.Test;
import static org.junit.Assert.*;

public final class StatisticsWindowTest {
    private static long millis(String iso) { return Instant.parse(iso).toEpochMilli(); }

    @Test public void hongKongDayStartsAtLocalMidnight() {
        StatisticsWindow day=StatisticsWindow.day(millis("2026-10-23T05:38:00Z"), TimeZone.getTimeZone("Asia/Hong_Kong"), 0);
        assertEquals(millis("2026-10-22T16:00:00Z"), day.startMillis);
        assertEquals(millis("2026-10-23T16:00:00Z"), day.endMillis);
    }
    @Test public void boundariesIncludeStartAndExcludeNextDay() {
        StatisticsWindow day=StatisticsWindow.day(millis("2026-10-23T05:38:00Z"), TimeZone.getTimeZone("Asia/Hong_Kong"), 0);
        assertTrue(day.contains(day.startMillis));
        assertTrue(day.contains(day.endMillis-1));
        assertFalse(day.contains(day.startMillis-1));
        assertFalse(day.contains(day.endMillis));
    }
    @Test public void sameInstantCanBelongToDifferentLocalDates() {
        long now=millis("2026-10-23T01:00:00Z");
        StatisticsWindow utc=StatisticsWindow.day(now, TimeZone.getTimeZone("UTC"), 0);
        StatisticsWindow newYork=StatisticsWindow.day(now, TimeZone.getTimeZone("America/New_York"), 0);
        assertEquals(millis("2026-10-23T00:00:00Z"), utc.startMillis);
        assertEquals(millis("2026-10-22T04:00:00Z"), newYork.startMillis);
    }
    @Test public void springClockChangeIsTwentyThreeHourCalendarDay() {
        StatisticsWindow day=StatisticsWindow.day(millis("2026-03-08T16:00:00Z"), TimeZone.getTimeZone("America/New_York"), 0);
        assertEquals(23L*60*60*1000, day.endMillis-day.startMillis);
        assertEquals(millis("2026-03-08T05:00:00Z"), day.startMillis);
        assertEquals(millis("2026-03-09T04:00:00Z"), day.endMillis);
    }
    @Test public void autumnClockChangeIsTwentyFiveHourCalendarDay() {
        StatisticsWindow day=StatisticsWindow.day(millis("2026-11-01T16:00:00Z"), TimeZone.getTimeZone("America/New_York"), 0);
        assertEquals(25L*60*60*1000, day.endMillis-day.startMillis);
    }
    @Test public void precedingWeekUsesCalendarDaysAcrossYearBoundary() {
        long now=millis("2026-01-02T09:00:00Z");
        TimeZone zone=TimeZone.getTimeZone("Asia/Hong_Kong");
        StatisticsWindow first=StatisticsWindow.day(now, zone, -6);
        assertEquals(millis("2025-12-26T16:00:00Z"), first.startMillis);
        for (int offset=-6; offset<0; offset++) {
            assertEquals(StatisticsWindow.day(now,zone,offset).endMillis,
                    StatisticsWindow.day(now,zone,offset+1).startMillis);
        }
    }
    @Test public void previousDayAcrossSpringChangeIsNotFixedTwentyFourHours() {
        long now=millis("2026-03-09T16:00:00Z");
        TimeZone zone=TimeZone.getTimeZone("America/New_York");
        StatisticsWindow previous=StatisticsWindow.day(now,zone,-1);
        assertEquals(23L*60*60*1000, previous.endMillis-previous.startMillis);
        assertEquals(StatisticsWindow.day(now,zone,0).startMillis,previous.endMillis);
    }
    @Test public void manualChecksAreNotIncomingSms() {
        assertTrue(StatisticsWindow.isSmsSource("incoming"));
        assertTrue(StatisticsWindow.isSmsSource("inbox"));
        assertFalse(StatisticsWindow.isSmsSource("manual"));
        assertFalse(StatisticsWindow.isSmsSource("unknown"));
        assertFalse(StatisticsWindow.isSmsSource(null));
    }
}
