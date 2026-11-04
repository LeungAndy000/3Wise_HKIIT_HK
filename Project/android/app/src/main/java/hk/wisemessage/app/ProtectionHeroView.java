package hk.wisemessage.app;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.view.View;

/** Lightweight, scalable artwork drawn locally; no bitmap, network or animation dependency. */
final class ProtectionHeroView extends View {
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path shield = new Path();
    private final Path symbol = new Path();
    private boolean ready;

    ProtectionHeroView(Context context) {
        super(context);
        setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);
    }

    void setReady(boolean value) { ready = value; invalidate(); }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.save();
        float scale = Math.min(getWidth() / 300f, getHeight() / 160f);
        canvas.translate(getWidth() / 2f, getHeight() / 2f);
        canvas.scale(scale, scale);
        int accent = ready ? Color.rgb(18, 128, 104) : Color.rgb(181, 48, 65);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(1);
        paint.setColor(ready ? 0x3032AE96 : 0x30C85D70);
        canvas.drawCircle(0, 0, 72, paint);
        canvas.drawCircle(0, 0, 56, paint);
        canvas.drawLine(-91, 0, 91, 0, paint);
        canvas.drawLine(0, -79, 0, 79, paint);
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(ready ? 0x2848BAA3 : 0x28CC6A7D);
        canvas.drawCircle(-72, -36, 4, paint);
        canvas.drawCircle(68, 31, 3, paint);
        canvas.drawCircle(59, -53, 2, paint);
        shield.reset();
        shield.moveTo(0, -52);
        shield.cubicTo(12, -48, 31, -40, 39, -34);
        shield.lineTo(39, 2);
        shield.cubicTo(39, 23, 20, 39, 0, 50);
        shield.cubicTo(-20, 39, -39, 23, -39, 2);
        shield.lineTo(-39, -34);
        shield.cubicTo(-31, -40, -12, -48, 0, -52);
        shield.close();
        paint.setColor(Color.WHITE);
        canvas.drawPath(shield, paint);
        paint.setStyle(Paint.Style.STROKE);
        paint.setColor(accent);
        paint.setStrokeWidth(4);
        canvas.drawPath(shield, paint);
        canvas.save();
        canvas.scale(.79f, .79f);
        paint.setStrokeWidth(1.5f);
        paint.setAlpha(80);
        canvas.drawPath(shield, paint);
        canvas.restore();
        paint.setAlpha(255);
        paint.setStrokeWidth(6);
        paint.setStrokeCap(Paint.Cap.ROUND);
        paint.setStrokeJoin(Paint.Join.ROUND);
        symbol.reset();
        if (ready) {
            symbol.moveTo(-14, 0); symbol.lineTo(-4, 10); symbol.lineTo(17, -13);
            canvas.drawPath(symbol, paint);
        } else {
            canvas.drawLine(0, -16, 0, 4, paint);
            paint.setStyle(Paint.Style.FILL);
            canvas.drawCircle(0, 17, 3, paint);
        }
        paint.setStrokeCap(Paint.Cap.BUTT);
        canvas.restore();
    }
}
