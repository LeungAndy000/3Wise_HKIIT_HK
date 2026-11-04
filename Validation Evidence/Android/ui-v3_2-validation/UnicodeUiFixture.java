package hk.wisemessage.qa;

import android.app.UiAutomation;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.os.Bundle;
import android.util.Base64;
import android.view.accessibility.AccessibilityNodeInfo;
import com.android.uiautomator.core.UiDevice;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;
import java.lang.reflect.Method;
import java.lang.reflect.Field;

/** Supplies fictional UTF-8 input through the real UI; never opens a database or model. */
public final class UnicodeUiFixture extends UiAutomatorTestCase {
    public void testSetManualMessage() throws Exception {
        String encoded = getParams().getString("message_b64");
        assertNotNull("Pass a fictional UTF-8 message using -e message_b64", encoded);
        String text = new String(Base64.decode(encoded, Base64.DEFAULT), "UTF-8");
        // Legacy UiObject.setText synthesizes key events and cannot represent Chinese.
        // Its shell bridge already owns UiAutomation: use the standard accessibility
        // ACTION_SET_TEXT operation, preserving the exact Unicode code points.
        Method bridgeMethod = UiDevice.class.getDeclaredMethod("getAutomatorBridge");
        bridgeMethod.setAccessible(true);
        Object bridge = bridgeMethod.invoke(getUiDevice());
        UiAutomation automation = null;
        for (Class<?> type = bridge.getClass(); type != null && automation == null; type = type.getSuperclass()) {
            for (Field field : type.getDeclaredFields()) {
                if (UiAutomation.class.isAssignableFrom(field.getType())) {
                    field.setAccessible(true);
                    automation = (UiAutomation) field.get(bridge);
                    break;
                }
            }
        }
        assertNotNull("Shell bridge has no UiAutomation connection", automation);
        AccessibilityServiceInfo service = automation.getServiceInfo();
        service.flags |= AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS;
        automation.setServiceInfo(service);
        automation.waitForIdle(200, 2000);
        AccessibilityNodeInfo root = automation.getRootInActiveWindow();
        AccessibilityNodeInfo input = findInput(root);
        assertNotNull("The real manual_input field must be visible", input);
        Bundle args = new Bundle();
        args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text);
        assertTrue("ACTION_SET_TEXT was rejected", input.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args));
        getUiDevice().waitForIdle();
        input.refresh();
        assertEquals("Unicode text changed during real UI input", text, input.getText().toString());
        System.out.println("WISEMESSAGE_UNICODE_FIXTURE_EXACT=true");
    }

    private AccessibilityNodeInfo findInput(AccessibilityNodeInfo node) {
        if (node == null) return null;
        if ("hk.wisemessage.app:id/manual_input".equals(node.getViewIdResourceName())) return node;
        for (int index = 0; index < node.getChildCount(); index++) {
            AccessibilityNodeInfo match = findInput(node.getChild(index));
            if (match != null) return match;
        }
        return null;
    }
}
