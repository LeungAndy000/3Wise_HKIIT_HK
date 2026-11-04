package hk.wisemessage.app;

import org.junit.Test;
import static org.junit.Assert.*;

public final class LanguageChoiceTest {
    @Test public void traditionalRegionsUseTraditionalScript() {
        for (String tag : new String[]{"zh-TW", "zh-HK", "zh-MO", "zh-Hant", "zh-Hant-HK"})
            assertEquals("zh-Hant", LanguageChoice.canonical(tag));
    }
    @Test public void simplifiedRegionsUseSimplifiedScript() {
        for (String tag : new String[]{"zh", "zh-CN", "zh-SG", "zh-Hans", "zh-Hans-CN"})
            assertEquals("zh-Hans", LanguageChoice.canonical(tag));
    }
    @Test public void explicitScriptTakesPrecedenceOverRegion() {
        assertEquals("zh-Hans", LanguageChoice.canonical("zh-Hans-HK"));
        assertEquals("zh-Hant", LanguageChoice.canonical("zh-Hant-CN"));
    }
    @Test public void englishVariantsUseEnglish() {
        assertEquals("en", LanguageChoice.canonical("en-GB"));
        assertEquals("en", LanguageChoice.canonical("en-US"));
    }
    @Test public void unsupportedOrEmptyChoiceUsesSystemLanguage() {
        assertEquals("", LanguageChoice.canonical(null));
        assertEquals("", LanguageChoice.canonical(""));
        assertEquals("", LanguageChoice.canonical("fr-FR"));
    }
    @Test public void pickerOrderRemainsStable() {
        assertEquals(0, LanguageChoice.indexOf(""));
        assertEquals(1, LanguageChoice.indexOf("zh-HK"));
        assertEquals(2, LanguageChoice.indexOf("zh-CN"));
        assertEquals(3, LanguageChoice.indexOf("en-US"));
    }
}
