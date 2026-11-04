package hk.wisemessage.app;

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;

/** Measures every action at its actual cell width before giving all cells the tallest height. */
final class EqualHeightActionGrid extends ViewGroup {
    private int columns = 2, cellWidth, cellHeight;

    EqualHeightActionGrid(Context context) { super(context); }

    @Override protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        int width = MeasureSpec.getSize(widthMeasureSpec);
        int gap = dp(10);
        int availableWidth = Math.max(0, width - getPaddingLeft() - getPaddingRight());
        columns = availableWidth < dp(316) || getResources().getConfiguration().fontScale > 1.3f ? 1 : 2;
        cellWidth = Math.max(0, (availableWidth - gap * (columns - 1)) / columns);
        cellHeight = 0;
        int visible = 0;
        for (int i = 0; i < getChildCount(); i++) {
            View child = getChildAt(i);
            if (child.getVisibility() == GONE) continue;
            child.measure(MeasureSpec.makeMeasureSpec(cellWidth, MeasureSpec.EXACTLY),
                    MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED));
            cellHeight = Math.max(cellHeight, child.getMeasuredHeight());
            visible++;
        }
        for (int i = 0; i < getChildCount(); i++) {
            View child = getChildAt(i);
            if (child.getVisibility() != GONE) child.measure(
                    MeasureSpec.makeMeasureSpec(cellWidth, MeasureSpec.EXACTLY),
                    MeasureSpec.makeMeasureSpec(cellHeight, MeasureSpec.EXACTLY));
        }
        int rows = (visible + columns - 1) / columns;
        int height = getPaddingTop() + getPaddingBottom() + rows * cellHeight + Math.max(0, rows - 1) * gap;
        setMeasuredDimension(resolveSize(width, widthMeasureSpec), resolveSize(height, heightMeasureSpec));
    }

    @Override protected void onLayout(boolean changed, int left, int top, int right, int bottom) {
        int gap = dp(10), position = 0;
        for (int i = 0; i < getChildCount(); i++) {
            View child = getChildAt(i);
            if (child.getVisibility() == GONE) continue;
            int x = getPaddingLeft() + position % columns * (cellWidth + gap);
            int y = getPaddingTop() + position / columns * (cellHeight + gap);
            child.layout(x, y, x + cellWidth, y + cellHeight);
            position++;
        }
    }

    @Override protected LayoutParams generateDefaultLayoutParams() {
        return new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT);
    }

    private int dp(int value) { return Math.round(getResources().getDisplayMetrics().density * value); }
}
