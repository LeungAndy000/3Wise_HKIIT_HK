package hk.wisemessage.app;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.view.View;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/** Seven local-day completion totals. TalkBack receives the same values as a textual summary. */
final class WeeklyChartView extends View {
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private List<MessageStore.DayStatistics> days = new ArrayList<>();
    private final List<String> labels = new ArrayList<>();
    private final List<String> counts = new ArrayList<>();

    WeeklyChartView(Context context) {
        super(context); setFocusable(true);
        paint.setTypeface(android.graphics.Typeface.create("sans-serif-medium", android.graphics.Typeface.NORMAL));
    }

    void setDays(List<MessageStore.DayStatistics> values) {
        days = new ArrayList<>(values);
        labels.clear(); counts.clear();
        StringBuilder summary = new StringBuilder();
        SimpleDateFormat date = new SimpleDateFormat("MMM d", AppLocale.displayLocale(getContext()));
        SimpleDateFormat label = new SimpleDateFormat("M/d", AppLocale.displayLocale(getContext()));
        for (MessageStore.DayStatistics day : days) {
            if (summary.length() > 0) summary.append("; ");
            summary.append(date.format(new Date(day.startMillis))).append(": ").append(day.checked);
            labels.add(label.format(new Date(day.startMillis)));
            counts.add(Long.toString(day.checked));
        }
        setContentDescription(getContext().getString(R.string.chart_accessibility, summary.toString()));
        invalidate();
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if (days.isEmpty()) return;
        float density = getResources().getDisplayMetrics().density;
        float font = getResources().getDisplayMetrics().scaledDensity;
        float slot = getWidth() / (float) days.size();
        float bottom = getHeight() - 28 * font;
        float top = 25 * font;
        long maximum = 1;
        for (MessageStore.DayStatistics day : days) maximum = Math.max(maximum, day.checked);
        paint.setTextAlign(Paint.Align.CENTER);
        boolean sparseLabels = getResources().getConfiguration().fontScale > 1.3f;
        for (int i = 0; i < days.size(); i++) {
            MessageStore.DayStatistics day = days.get(i);
            float center = slot * (i + .5f);
            float width = Math.min(26 * density, slot * .54f);
            float height = (bottom - top) * day.checked / maximum;
            paint.setColor(i == days.size() - 1 ? 0xFF137C6B : 0xFFA5D8CB);
            canvas.drawRoundRect(center - width / 2, bottom - Math.max(3 * density, height),
                    center + width / 2, bottom, 5 * density, 5 * density, paint);
            paint.setColor(0xFF365C53);
            paint.setTextSize(11 * font);
            if (!sparseLabels || i % 3 == 0) canvas.drawText(counts.get(i), center, bottom - height - 8 * density, paint);
            paint.setColor(Color.rgb(96, 116, 111));
            paint.setTextSize(10 * font);
            if (!sparseLabels || i % 3 == 0) canvas.drawText(labels.get(i), center, bottom + 20 * font, paint);
        }
    }
}
