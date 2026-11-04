package hk.wisemessage.app;

import java.util.Locale;

/** Platform-independent language identifiers; never changes model inputs or labels. */
final class LanguageChoice {
    static final String[] TAGS = {"", "zh-Hant", "zh-Hans", "en"};
    private LanguageChoice() {}

    static String canonical(String languageTag) {
        if (languageTag == null || languageTag.isEmpty()) return "";
        Locale locale = Locale.forLanguageTag(languageTag);
        if ("en".equals(locale.getLanguage())) return "en";
        if (!"zh".equals(locale.getLanguage())) return "";
        if ("Hant".equals(locale.getScript())) return "zh-Hant";
        if ("Hans".equals(locale.getScript())) return "zh-Hans";
        String region = locale.getCountry();
        return "TW".equals(region) || "HK".equals(region) || "MO".equals(region) ? "zh-Hant" : "zh-Hans";
    }

    static int indexOf(String languageTag) {
        String canonical = canonical(languageTag);
        for (int i = 0; i < TAGS.length; i++) if (TAGS[i].equals(canonical)) return i;
        return 0;
    }
}
