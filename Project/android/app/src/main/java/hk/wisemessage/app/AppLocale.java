package hk.wisemessage.app;

import android.app.LocaleManager;
import android.content.Context;
import android.content.res.Configuration;
import android.os.Build;
import android.os.LocaleList;
import java.util.Locale;

/** Explicit app language on API 26+, synchronized with Android 13 app-language settings. */
final class AppLocale {
    private static final String PREFERENCES = "app_language";
    private static final String KEY = "selected_language";
    private AppLocale() {}

    static String selected(Context context) {
        if (Build.VERSION.SDK_INT >= 33) {
            LocaleManager manager = context.getSystemService(LocaleManager.class);
            if (manager != null) {
                LocaleList locales = manager.getApplicationLocales();
                return locales.isEmpty() ? "" : LanguageChoice.canonical(locales.get(0).toLanguageTag());
            }
        }
        return LanguageChoice.canonical(context.getSharedPreferences(PREFERENCES, Context.MODE_PRIVATE).getString(KEY, ""));
    }

    static Context wrap(Context context) {
        String language = selected(context);
        if (language.isEmpty()) return context;
        Configuration configuration = new Configuration(context.getResources().getConfiguration());
        configuration.setLocales(LocaleList.forLanguageTags(language));
        return context.createConfigurationContext(configuration);
    }

    static void select(Context context, String languageTag) {
        String language = LanguageChoice.canonical(languageTag);
        context.getSharedPreferences(PREFERENCES, Context.MODE_PRIVATE).edit().putString(KEY, language).apply();
        if (Build.VERSION.SDK_INT >= 33) {
            LocaleManager manager = context.getSystemService(LocaleManager.class);
            if (manager != null) manager.setApplicationLocales(LocaleList.forLanguageTags(language));
        }
    }

    static Locale displayLocale(Context context) {
        return wrap(context).getResources().getConfiguration().getLocales().get(0);
    }
}
