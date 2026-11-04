package hk.wisemessage.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Toast;
import java.text.DateFormat;
import java.text.NumberFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import hk.wisemessage.app.ml.LocalMessageClassifier;
import hk.wisemessage.app.ml.Prediction;

/** Offline dashboard. Reads consented SMS; never opens links or changes phone SMS. */
public final class MainActivity extends Activity {
    private enum Page { HOME, MESSAGES, INBOX, RESULTS, MANUAL, STATISTICS, SETTINGS }
    private enum InboxAction { NONE, READ, SCAN }
    private static final int REQUEST_MONITOR = 10, REQUEST_INBOX = 11, REQUEST_NOTIFICATION = 12, REQUEST_RECEIVE = 13;
    private static final int INK = 0xFF183E35, MUTED = 0xFF60746E, GREEN = 0xFF087D52;
    private static final int RED = 0xFFB6383C, AMBER = 0xFF99630D, BACKGROUND = 0xFFF3F8F6;
    private static final int TEAL = 0xFF087D70, BORDER = 0xFFDCE9E3;
    private static final int LIST_PAGE_SIZE = 20;
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private final Handler main = new Handler(Looper.getMainLooper());
    private Page currentPage = Page.HOME;
    private InboxAction pendingInboxAction = InboxAction.NONE;
    private LinearLayout root, page, navigation, history, inboxList, protectionCard, importProgressCard;
    private ScrollView scroll;
    private TextView status, protectionTitle, receivedCount, checkedCount, receivedNote, progressText, statisticsEmpty, legacyNote;
    private TableLayout statisticsTable, weeklyTable;
    private ProtectionHeroView hero;
    private WeeklyChartView chart;
    private Switch monitor, notificationSwitch;
    private EditText input;
    private TextView result;
    private Button checkButton, loadMoreButton, inboxPreviousButton, inboxRefreshButton, resultsPreviousButton, resultsNextButton, stopButton;
    private TextView inboxPageStatus, resultsPageStatus;
    private ResultFilter resultsFilter = ResultFilter.HARMFUL;
    private MessageStore.ResultPage resultsPage;
    private InboxAccess.InboxPage inboxPage;
    private final List<Long> resultsCursors = new ArrayList<>();
    private final List<InboxAccess.Position> inboxCursors = new ArrayList<>();
    private long resultsBeforeId, inboxBeforeReceived = -1, inboxBeforeId = -1;
    private boolean loadingResults, inboxConsentAccepted, inboxResetPending;
    private int resultsGeneration;
    private String renderedResults = "";
    private final List<InboxAccess.Sms> inboxRows = new ArrayList<>();
    private MessageStore.Statistics statistics;
    private long inboxReceivedToday = -1, pendingDetailsId = -1;
    private boolean updatingSwitch, refreshing, loadingInbox, inboxLoaded, manualBusy;
    private Prediction lastPrediction;
    private boolean lastManualFailed;
    private final Runnable refresh = new Runnable() {
        @Override public void run() {
            updateProtectionStatus(); updateImportProgress(); refreshData();
            main.postDelayed(this, 3000);
        }
    };

    @Override protected void attachBaseContext(Context base) { super.attachBaseContext(AppLocale.wrap(base)); }
    @Override public void onCreate(Bundle savedState) {
        super.onCreate(savedState);
        if (savedState != null) {
            try { currentPage = Page.valueOf(savedState.getString("page", Page.HOME.name())); }
            catch (IllegalArgumentException ignored) { currentPage = Page.HOME; }
            try { pendingInboxAction = InboxAction.valueOf(savedState.getString("inbox_action", InboxAction.NONE.name())); }
            catch (IllegalArgumentException ignored) { pendingInboxAction = InboxAction.NONE; }
            try { resultsFilter = ResultFilter.valueOf(savedState.getString("results_filter", ResultFilter.HARMFUL.name())); }
            catch (IllegalArgumentException ignored) { resultsFilter = ResultFilter.HARMFUL; }
            resultsBeforeId = savedState.getLong("results_before", 0);
            long[] resultPositions = savedState.getLongArray("result_cursors");
            if (resultPositions != null) for (long position : resultPositions) resultsCursors.add(position);
            inboxBeforeReceived = savedState.getLong("inbox_before_date", -1);
            inboxBeforeId = savedState.getLong("inbox_before_id", -1);
            long[] inboxPositions = savedState.getLongArray("inbox_cursors");
            if (inboxPositions != null) for (int i = 0; i + 1 < inboxPositions.length; i += 2)
                inboxCursors.add(new InboxAccess.Position(inboxPositions[i], inboxPositions[i + 1]));
            inboxConsentAccepted = savedState.getBoolean("inbox_consent", false);
        }
        ScamNotifications.ensureChannel(this);
        pendingDetailsId = getIntent().getLongExtra("record_id", -1);
        buildShell(); showPage(currentPage);
        if (currentPage == Page.INBOX && inboxConsentAccepted && has(Manifest.permission.READ_SMS)) loadInboxPage(false);
        if (Build.VERSION.SDK_INT >= 33) getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT, this::navigateBack);
        worker.execute(() -> { try { ScanScheduler.resumePending(this); } catch (RuntimeException ignored) {} });
    }
    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent); setIntent(intent);
        pendingDetailsId = intent.getLongExtra("record_id", -1);
        if (pendingDetailsId > 0) showPendingDetails();
    }
    @Override protected void onSaveInstanceState(Bundle state) {
        state.putString("page", currentPage.name());
        state.putString("inbox_action", pendingInboxAction.name());
        state.putString("results_filter", resultsFilter.name()); state.putLong("results_before", resultsBeforeId);
        long[] resultPositions = new long[resultsCursors.size()];
        for (int i = 0; i < resultPositions.length; i++) resultPositions[i] = resultsCursors.get(i);
        state.putLongArray("result_cursors", resultPositions);
        state.putLong("inbox_before_date", inboxBeforeReceived); state.putLong("inbox_before_id", inboxBeforeId);
        long[] inboxPositions = new long[inboxCursors.size() * 2];
        for (int i = 0; i < inboxCursors.size(); i++) {
            inboxPositions[i * 2] = inboxCursors.get(i).received; inboxPositions[i * 2 + 1] = inboxCursors.get(i).id;
        }
        state.putLongArray("inbox_cursors", inboxPositions); state.putBoolean("inbox_consent", inboxConsentAccepted);
        // Never put SMS bodies or manual drafts into Android's saved-state bundle.
        super.onSaveInstanceState(state);
    }
    @Override protected void onResume() {
        super.onResume(); main.removeCallbacks(refresh); main.post(refresh); main.post(this::showPendingDetails);
        if (currentPage == Page.SETTINGS) showPage(Page.SETTINGS);
    }
    @Override protected void onPause() { main.removeCallbacks(refresh); super.onPause(); }
    @Override protected void onDestroy() { main.removeCallbacks(refresh); worker.shutdown(); super.onDestroy(); }
    // API 26–32 fallback. API 33+ uses the registered platform dispatcher above.
    @SuppressLint("GestureBackNavigation")
    @SuppressWarnings("deprecation") @Override public void onBackPressed() { navigateBack(); }
    private void navigateBack() {
        if (currentPage == Page.HOME) finish();
        else showPage(currentPage == Page.MANUAL || currentPage == Page.INBOX || currentPage == Page.RESULTS ? Page.MESSAGES : Page.HOME);
    }

    private void buildShell() {
        root = column(); root.setBackgroundColor(BACKGROUND);
        LinearLayout header = new LinearLayout(this); header.setGravity(Gravity.CENTER_VERTICAL);
        header.setPadding(dp(22), dp(14), dp(18), dp(12));
        header.addView(icon(R.drawable.ic_shield, TEAL, 28), new LinearLayout.LayoutParams(dp(30), dp(32)));
        LinearLayout wordmark = column(); wordmark.setPadding(dp(10), 0, 0, 0);
        wordmark.addView(text("WiseMessage", 23, INK, true));
        header.addView(wordmark, new LinearLayout.LayoutParams(0, -2, 1));
        LinearLayout settings = column(); settings.setGravity(Gravity.CENTER);
        settings.setContentDescription(getString(R.string.settings_title));
        settings.addView(icon(R.drawable.ic_settings, INK, 23));
        settings.setBackground(clickableBackground(Color.WHITE, BORDER, 16));
        settings.setFocusable(true); settings.setOnClickListener(v -> showPage(Page.SETTINGS));
        header.addView(settings, new LinearLayout.LayoutParams(dp(48), dp(48))); root.addView(header);
        scroll = new ScrollView(this); scroll.setFillViewport(true); scroll.setClipToPadding(false);
        page = column(); page.setPadding(dp(22), dp(4), dp(22), dp(24));
        scroll.addView(page, new ScrollView.LayoutParams(-1, -2));
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        navigation = new LinearLayout(this); navigation.setGravity(Gravity.CENTER_VERTICAL);
        navigation.setBackgroundColor(Color.WHITE); navigation.setElevation(dp(10));
        navigation.setPadding(dp(8), dp(8), dp(8), dp(7));
        navigation.setContentDescription(getString(R.string.menu_label));
        root.addView(navigation, new LinearLayout.LayoutParams(-1, -2));
        root.setOnApplyWindowInsetsListener((view, insets) -> {
            int left, top, right, bottom;
            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                android.graphics.Insets ime = insets.getInsets(WindowInsets.Type.ime());
                left = bars.left; top = bars.top; right = bars.right; bottom = Math.max(bars.bottom, ime.bottom);
            } else {
                left = insets.getSystemWindowInsetLeft(); top = insets.getSystemWindowInsetTop();
                right = insets.getSystemWindowInsetRight(); bottom = insets.getSystemWindowInsetBottom();
            }
            root.setPadding(left, top, right, bottom); return insets;
        });
        setContentView(root); root.requestApplyInsets();
    }

    private void showPage(Page destination) {
        currentPage = destination; page.removeAllViews(); page.setId(View.NO_ID);
        status = null; protectionTitle = null; protectionCard = null; hero = null;
        receivedCount = null; checkedCount = null; receivedNote = null; history = null; inboxList = null;
        progressText = null; importProgressCard = null; statisticsEmpty = null; legacyNote = null;
        statisticsTable = null; weeklyTable = null; chart = null; monitor = null; notificationSwitch = null;
        inboxPageStatus = null; resultsPageStatus = null; inboxPreviousButton = null; resultsPreviousButton = null; resultsNextButton = null;
        inboxRefreshButton = null;
        renderedResults = "";
        input = null; result = null; checkButton = null; loadMoreButton = null; stopButton = null;
        switch (destination) {
            case HOME: buildHome(); break;
            case MESSAGES: buildMessages(); break;
            case INBOX: buildInbox(); break;
            case RESULTS: buildResults(); break;
            case MANUAL: buildManual(); break;
            case STATISTICS: buildStatistics(); break;
            case SETTINGS: buildSettings(); break;
        }
        buildNavigation(); updateProtectionStatus(); updateImportProgress(); renderData(); refreshData();
        scroll.post(() -> scroll.scrollTo(0, 0));
    }
    private void buildNavigation() {
        navigation.removeAllViews();
        nav(Page.HOME, R.id.nav_home, R.string.nav_home, R.drawable.ic_dashboard);
        nav(Page.MESSAGES, R.id.nav_messages, R.string.nav_messages, R.drawable.ic_messages);
        nav(Page.STATISTICS, R.id.nav_statistics, R.string.nav_statistics, R.drawable.ic_chart);
        nav(Page.SETTINGS, R.id.nav_settings, R.string.nav_settings, R.drawable.ic_settings);
    }
    private void nav(Page destination, int id, int label, int drawable) {
        boolean selected = currentPage == destination || (destination == Page.MESSAGES
                && (currentPage == Page.MANUAL || currentPage == Page.INBOX || currentPage == Page.RESULTS));
        LinearLayout tab = column(); tab.setId(id); tab.setGravity(Gravity.CENTER); tab.setMinimumHeight(dp(62));
        tab.setPadding(dp(2), dp(7), dp(2), dp(6));
        tab.setBackground(clickableBackground(selected ? 0xFFE4F3ED : Color.WHITE, Color.TRANSPARENT, 14));
        tab.addView(icon(drawable, selected ? TEAL : MUTED, 23));
        TextView caption = text(getString(label), 12, selected ? TEAL : MUTED, selected);
        caption.setGravity(Gravity.CENTER); caption.setPadding(0, dp(5), 0, 0); tab.addView(caption);
        tab.setSelected(selected); tab.setFocusable(true); tab.setContentDescription(selected
                ? getString(R.string.nav_accessibility_current, getString(label)) : getString(label));
        tab.setOnClickListener(v -> showPage(destination));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, -2, 1); params.setMargins(dp(3), 0, dp(3), 0);
        navigation.addView(tab, params);
    }

    private void buildHome() {
        page.setId(R.id.home_screen);
        TextView date = text(DateFormat.getDateInstance(DateFormat.FULL, AppLocale.displayLocale(this)).format(new Date()), 13, MUTED, false);
        date.setPadding(0, dp(6), 0, dp(12)); page.addView(date);
        protectionCard = panel(page); protectionCard.setId(R.id.protection_card);
        protectionCard.setPadding(dp(21), dp(9), dp(21), dp(20));
        hero = new ProtectionHeroView(this); protectionCard.addView(hero, new LinearLayout.LayoutParams(-1, dp(152)));
        protectionTitle = text("", 24, RED, true); protectionTitle.setId(R.id.protection_title);
        protectionTitle.setGravity(Gravity.CENTER); protectionCard.addView(protectionTitle);
        status = text("", 15, MUTED, false); status.setId(R.id.status_text); status.setGravity(Gravity.CENTER);
        status.setPadding(0, dp(9), 0, dp(12)); protectionCard.addView(status);
        Button repair = primaryButton(R.string.protection_fix); repair.setOnClickListener(v -> showPage(Page.SETTINGS)); protectionCard.addView(repair);
        sectionTitle(R.string.daily_title);
        LinearLayout daily = panel(page); daily.setOrientation(LinearLayout.HORIZONTAL); daily.setPadding(dp(18), dp(18), dp(18), dp(18));
        receivedCount = metricCell(daily, R.string.daily_received); receivedCount.setId(R.id.daily_received_count);
        View divider = new View(this); divider.setBackgroundColor(BORDER); daily.addView(divider, new LinearLayout.LayoutParams(dp(1), dp(62)));
        checkedCount = metricCell(daily, R.string.daily_checked); checkedCount.setId(R.id.daily_checked_count);
        receivedNote = note(R.string.daily_received_unavailable); page.addView(receivedNote);
        sectionTitle(R.string.actions_title);
        EqualHeightActionGrid actions = new EqualHeightActionGrid(this); actions.setId(R.id.dashboard_actions);
        actions.addView(actionCard(R.id.scan_all_button, R.drawable.ic_scan, R.string.action_scan_all, R.string.action_scan_all_description, this::confirmFullScan));
        actions.addView(actionCard(R.id.read_sms_button, R.drawable.ic_messages, R.string.action_read_sms, R.string.action_read_sms_description, this::confirmReadInbox));
        actions.addView(actionCard(R.id.manual_nav_button, R.drawable.ic_edit, R.string.action_manual, R.string.action_manual_description, () -> showPage(Page.MANUAL)));
        actions.addView(actionCard(R.id.statistics_button, R.drawable.ic_chart, R.string.action_statistics, R.string.action_statistics_description, () -> showPage(Page.STATISTICS)));
        LinearLayout.LayoutParams actionParams = new LinearLayout.LayoutParams(-1, -2); actionParams.topMargin = dp(10);
        page.addView(actions, actionParams);
        addImportProgress();
    }

    private void buildMessages() {
        page.setId(R.id.messages_screen); pageHeading(R.string.messages_hub_title, R.string.messages_hub_subtitle);
        action(page, true, R.id.inbox_entry_button, R.drawable.ic_messages, R.string.open_inbox,
                R.string.open_inbox_description, this::confirmReadInbox);
        action(page, true, R.id.results_entry_button, R.drawable.ic_chart, R.string.open_results,
                R.string.open_results_description, () -> showPage(Page.RESULTS));
        action(page, true, R.id.scan_all_button, R.drawable.ic_scan, R.string.action_scan_all, R.string.action_scan_all_description, this::confirmFullScan);
        action(page, true, R.id.manual_nav_button, R.drawable.ic_edit, R.string.action_manual, R.string.action_manual_description, () -> showPage(Page.MANUAL));
        addImportProgress();
    }
    private void buildInbox() {
        page.setId(R.id.inbox_screen); pageHeading(R.string.open_inbox);
        LinearLayout inbox = titledPanel(R.string.inbox_read_title);
        Button read = secondaryButton(R.string.refresh); read.setId(R.id.inbox_refresh_button);
        inboxRefreshButton = read;
        read.setOnClickListener(v -> confirmReadInbox()); inbox.addView(read);
        inboxList = column(); inboxList.setId(R.id.inbox_container); inbox.addView(inboxList);
        inboxPageStatus = note(R.string.pagination_empty); inboxPageStatus.setId(R.id.inbox_page_status); inbox.addView(inboxPageStatus);
        LinearLayout controls = new LinearLayout(this); controls.setGravity(Gravity.CENTER_VERTICAL);
        inboxPreviousButton = secondaryButton(R.string.pagination_previous); inboxPreviousButton.setId(R.id.inbox_previous_button);
        inboxPreviousButton.setOnClickListener(v -> previousInboxPage());
        controls.addView(inboxPreviousButton, pagerParams());
        loadMoreButton = secondaryButton(R.string.pagination_next); loadMoreButton.setId(R.id.inbox_next_button);
        loadMoreButton.setOnClickListener(v -> nextInboxPage()); controls.addView(loadMoreButton, pagerParams()); inbox.addView(controls);
        renderInboxRows();
    }
    private void buildResults() {
        page.setId(R.id.results_screen); pageHeading(R.string.detection_results_title);
        LinearLayout checks = panel(page);
        TextView filterLabel = text(getString(R.string.result_filter_title), 16, INK, true); checks.addView(filterLabel);
        Spinner filter = new Spinner(this); filter.setId(R.id.results_filter); filter.setMinimumHeight(dp(56));
        String[] labels = {getString(R.string.filter_harmful), getString(R.string.filter_normal), getString(R.string.filter_review), getString(R.string.filter_all)};
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, labels);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item); filter.setAdapter(adapter);
        filter.setSelection(filterIndex(resultsFilter)); filter.setContentDescription(getString(R.string.result_filter_title));
        checks.addView(filter, new LinearLayout.LayoutParams(-1, -2));
        filter.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                ResultFilter selected = filterAt(position);
                if (resultsFilter != selected) { resultsFilter = selected; resetResultsPaging(); loadResults(true); }
            }
            @Override public void onNothingSelected(AdapterView<?> parent) {}
        });
        history = column(); history.setId(R.id.history_container); checks.addView(history);
        resultsPageStatus = note(R.string.pagination_empty); resultsPageStatus.setId(R.id.results_page_status); checks.addView(resultsPageStatus);
        LinearLayout controls = new LinearLayout(this); controls.setGravity(Gravity.CENTER_VERTICAL);
        resultsPreviousButton = secondaryButton(R.string.pagination_previous); resultsPreviousButton.setId(R.id.results_previous_button);
        resultsPreviousButton.setOnClickListener(v -> previousResultsPage()); controls.addView(resultsPreviousButton, pagerParams());
        resultsNextButton = secondaryButton(R.string.pagination_next); resultsNextButton.setId(R.id.results_next_button);
        resultsNextButton.setOnClickListener(v -> nextResultsPage()); controls.addView(resultsNextButton, pagerParams()); checks.addView(controls);
        Button reload = secondaryButton(R.string.refresh); reload.setId(R.id.results_refresh_button);
        reload.setOnClickListener(v -> {
            worker.execute(() -> { try { ScanScheduler.resumePending(this); } catch (RuntimeException ignored) {} });
            resetResultsPaging(); loadResults(true); refreshData();
        }); checks.addView(reload); renderResults(); loadResults(false);
    }
    private LinearLayout.LayoutParams pagerParams() {
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, -2, 1);
        params.setMargins(dp(3), dp(8), dp(3), 0); return params;
    }
    private static ResultFilter filterAt(int index) {
        return index == 1 ? ResultFilter.LOW_RISK : index == 2 ? ResultFilter.REVIEW : index == 3 ? ResultFilter.ALL : ResultFilter.HARMFUL;
    }
    private static int filterIndex(ResultFilter filter) {
        return filter == ResultFilter.LOW_RISK ? 1 : filter == ResultFilter.REVIEW ? 2 : filter == ResultFilter.ALL ? 3 : 0;
    }
    private void resetResultsPaging() {
        resultsBeforeId = 0; resultsCursors.clear(); resultsPage = null; renderedResults = "";
    }
    private void nextResultsPage() {
        if (loadingResults || resultsPage == null || !resultsPage.hasMore) return;
        resultsCursors.add(resultsBeforeId); resultsBeforeId = resultsPage.nextBeforeId;
        resultsPage = null; renderedResults = ""; loadResults(true); scroll.smoothScrollTo(0, 0);
    }
    private void previousResultsPage() {
        if (loadingResults || resultsCursors.isEmpty()) return;
        resultsBeforeId = resultsCursors.remove(resultsCursors.size() - 1);
        resultsPage = null; renderedResults = ""; loadResults(true); scroll.smoothScrollTo(0, 0);
    }
    private void loadResults(boolean force) {
        if (isDestroyed() || (loadingResults && !force)) return;
        final int generation = ++resultsGeneration;
        final ResultFilter selected = resultsFilter;
        final long before = resultsBeforeId;
        loadingResults = true; renderResults();
        worker.execute(() -> {
            MessageStore.ResultPage loaded = null;
            try { loaded = MessageStore.get(this).results(selected, before, LIST_PAGE_SIZE); }
            catch (RuntimeException ignored) {}
            final MessageStore.ResultPage snapshot = loaded;
            main.post(() -> {
                if (isDestroyed() || generation != resultsGeneration) return;
                loadingResults = false;
                if (selected != resultsFilter || before != resultsBeforeId) return;
                if (snapshot != null && before > 0 && (snapshot.records.isEmpty()
                        || (long) resultsCursors.size() * LIST_PAGE_SIZE >= snapshot.totalMatched)) {
                    resetResultsPaging(); loadResults(true); return;
                }
                resultsPage = snapshot; renderResults();
            });
        });
    }
    private void renderResults() {
        if (history == null) return;
        StringBuilder signature = new StringBuilder(resultsFilter.name()).append(':').append(resultsBeforeId);
        if (resultsPage != null) {
            signature.append(':').append(resultsPage.totalMatched);
            for (MessageStore.Record record : resultsPage.records)
                signature.append('|').append(record.id).append(':').append(record.state).append(':').append(record.label)
                        .append(':').append(record.isScam).append(':').append(record.isUnwanted).append(':').append(record.decisionMetadataValid);
        } else signature.append(loadingResults ? ":loading" : ":failed");
        if (!signature.toString().equals(renderedResults)) {
            history.removeAllViews(); renderedResults = signature.toString();
            if (resultsPage == null) history.addView(note(loadingResults ? R.string.results_loading : R.string.results_load_failed));
            else if (resultsPage.records.isEmpty()) history.addView(note(R.string.results_empty_filtered));
            else for (MessageStore.Record record : resultsPage.records) {
                String sender = record.sender.isEmpty() ? getString(sourceName(record.source)) : record.sender;
                TextView row = recordRow(sender + " · " + formatDate(record.received)
                        + "\n" + getString(recordCaption(record)), recordColor(record));
                row.setTag(record); row.setOnClickListener(v -> showRecord(record)); history.addView(row);
            }
        }
        if (resultsPreviousButton != null) resultsPreviousButton.setEnabled(!loadingResults && !resultsCursors.isEmpty());
        if (resultsNextButton != null) resultsNextButton.setEnabled(!loadingResults && resultsPage != null && resultsPage.hasMore);
        if (resultsPageStatus != null) resultsPageStatus.setText(resultsPage == null || resultsPage.records.isEmpty()
                ? getString(R.string.pagination_empty) : getString(R.string.pagination_results_page,
                resultsCursors.size() + 1, resultsPage.records.size(), resultsPage.totalMatched));
    }
    private void buildManual() {
        page.setId(R.id.manual_screen); pageHeading(R.string.action_manual);
        LinearLayout manual = panel(page);
        input = new EditText(this); input.setId(R.id.manual_input); input.setHint(R.string.manual_hint);
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE | InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
        input.setMinLines(5); input.setTextSize(18); input.setTextColor(INK); input.setHintTextColor(MUTED);
        input.setGravity(Gravity.TOP); input.setSaveEnabled(false); input.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_NO);
        input.setBackground(shape(Color.WHITE, BORDER, 15)); input.setPadding(dp(14), dp(14), dp(14), dp(14));
        manual.addView(input, new LinearLayout.LayoutParams(-1, -2));
        checkButton = primaryButton(R.string.check_message); checkButton.setId(R.id.classify_button);
        checkButton.setEnabled(!manualBusy); checkButton.setOnClickListener(v -> classifyManual()); manual.addView(checkButton);
        result = text("", 18, INK, true); result.setId(R.id.result_text); result.setTextIsSelectable(true);
        result.setPadding(0, dp(16), 0, dp(8)); result.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        manual.addView(result); renderManualResult();
    }
    private void buildStatistics() {
        page.setId(R.id.statistics_screen); pageHeading(R.string.statistics_title);
        LinearLayout totals = panel(page);
        statisticsTable = statisticsTable(totals, R.id.stats_table);
        tableHeader(statisticsTable, R.id.stats_table_header, R.string.stats_metric, R.string.stats_today, R.string.stats_all_time);
        statisticsRow(R.id.stats_checked_row, R.string.stats_checked);
        statisticsRow(R.id.stats_normal_row, R.string.stats_normal);
        statisticsRow(R.id.stats_spam_row, R.string.stats_spam);
        statisticsRow(R.id.stats_scam_row, R.string.stats_scam);
        statisticsRow(R.id.stats_review_row, R.string.stats_review);
        statisticsRow(R.id.stats_pending_row, R.string.stats_pending);
        statisticsRow(R.id.stats_failed_row, R.string.stats_failed);
        statisticsEmpty = note(R.string.stats_empty); statisticsEmpty.setId(R.id.stats_empty_state); totals.addView(statisticsEmpty);
        legacyNote = note(R.string.stats_unknown_date); legacyNote.setId(R.id.stats_legacy_note); legacyNote.setVisibility(View.GONE); totals.addView(legacyNote);
        LinearLayout week = titledPanel(R.string.statistics_7_days);
        chart = new WeeklyChartView(this); chart.setId(R.id.stats_chart);
        int chartHeight = Math.round(200 * Math.max(1f, getResources().getConfiguration().fontScale));
        week.addView(chart, new LinearLayout.LayoutParams(-1, dp(chartHeight)));
        weeklyTable = statisticsTable(week, R.id.stats_week_table);
        tableHeader(weeklyTable, R.id.stats_week_header, R.string.stats_date, R.string.stats_checked);
    }
    private void buildSettings() {
        page.setId(R.id.settings_screen); pageHeading(R.string.settings_title, R.string.settings_subtitle);
        LinearLayout protection = titledPanel(R.string.settings_protection);
        monitor = toggle(protection, R.id.monitor_switch, R.string.monitor_toggle);
        monitor.setOnCheckedChangeListener((button, enabled) -> {
            if (updatingSwitch) return;
            if (!enabled) { AppPreferences.setMonitoring(this, false); updateProtectionStatus(); }
            else {
                setSwitches();
                new AlertDialog.Builder(this).setTitle(R.string.consent_title).setMessage(R.string.consent_body)
                        .setNegativeButton(R.string.cancel, null).setPositiveButton(R.string.enable, (dialog, which) -> enableMonitoring()).show();
            }
        });
        status = note(R.string.monitor_off); status.setId(R.id.status_text); protection.addView(status);
        protection.addView(note(R.string.monitor_limits));
        if (Build.VERSION.SDK_INT >= 37) protection.addView(note(R.string.otp_delay));
        LinearLayout permissions = titledPanel(R.string.settings_permissions);
        Button sms = secondaryButton(R.string.grant_sms_permission); sms.setId(R.id.grant_sms_button);
        sms.setOnClickListener(v -> {
            if (has(Manifest.permission.RECEIVE_SMS)) openAppSettings();
            else requestPermissions(new String[]{Manifest.permission.RECEIVE_SMS}, REQUEST_RECEIVE);
        }); permissions.addView(sms);
        permissions.addView(note(R.string.permission_receive_help));
        Button inbox = secondaryButton(R.string.grant_inbox_access); inbox.setId(R.id.grant_inbox_button);
        inbox.setOnClickListener(v -> {
            if (has(Manifest.permission.READ_SMS)) openAppSettings();
            else { pendingInboxAction = InboxAction.NONE; requestPermissions(new String[]{Manifest.permission.READ_SMS}, REQUEST_INBOX); }
        }); permissions.addView(inbox);
        TextView grants = text(getString(R.string.receive_permission_status) + ": " + permissionText(has(Manifest.permission.RECEIVE_SMS))
                + "\n" + getString(R.string.read_permission_status) + ": " + permissionText(has(Manifest.permission.READ_SMS)), 14, MUTED, false);
        grants.setPadding(0, dp(10), 0, 0); permissions.addView(grants);
        Button system = secondaryButton(R.string.app_settings); system.setOnClickListener(v -> openAppSettings()); permissions.addView(system);
        LinearLayout alerts = titledPanel(R.string.settings_notifications);
        notificationSwitch = toggle(alerts, R.id.notification_switch, R.string.notifications_toggle);
        notificationSwitch.setOnCheckedChangeListener((button, enabled) -> {
            if (updatingSwitch) return;
            AppPreferences.setNotificationsEnabled(this, enabled); updateProtectionStatus();
            if (enabled && !ScamNotifications.systemAllowed(this)) requestNotifications();
        });
        Button grant = secondaryButton(R.string.allow_notifications); grant.setId(R.id.notification_button);
        grant.setOnClickListener(v -> requestNotifications()); alerts.addView(grant);
        Button test = secondaryButton(R.string.notification_test); test.setId(R.id.notification_test_button);
        test.setOnClickListener(v -> toast(ScamNotifications.showTest(this) ? R.string.notification_test_sent : R.string.notification_blocked)); alerts.addView(test);
        alerts.addView(text(getString(R.string.notification_permission_title) + ": "
                + permissionText(ScamNotifications.systemAllowed(this)), 14, MUTED, false));
        LinearLayout language = titledPanel(R.string.settings_language);
        Button languages = secondaryButton(R.string.language_button); languages.setId(R.id.language_button);
        languages.setOnClickListener(v -> showLanguagePicker()); language.addView(languages); language.addView(note(R.string.language_help));
        LinearLayout privacy = titledPanel(R.string.privacy_title); privacy.addView(note(R.string.privacy_body));
        LinearLayout explanations = titledPanel(R.string.settings_check_details); explanations.setId(R.id.settings_explanations);
        explanations.addView(text(getString(R.string.model_brand), 16, INK, true));
        explanations.addView(note(R.string.not_guarantee)); explanations.addView(note(R.string.global_scan_note));
        explanations.addView(note(R.string.results_filter_note)); explanations.addView(note(R.string.inbox_privacy_hint));
        explanations.addView(note(R.string.inbox_page_note)); explanations.addView(note(R.string.results_page_note));
        LinearLayout statisticsHelp = titledPanel(R.string.statistics_title);
        statisticsHelp.addView(note(R.string.stats_local_scope)); statisticsHelp.addView(note(R.string.stats_retention_note));
        statisticsHelp.addView(note(R.string.daily_received_note)); statisticsHelp.addView(note(R.string.daily_checked_note));
        statisticsHelp.addView(note(R.string.stats_pending_scope));
    }

    private String permissionText(boolean granted) { return getString(granted ? R.string.permission_granted : R.string.permission_missing); }
    private void showLanguagePicker() {
        String[] names = {getString(R.string.language_system), "繁體中文", "简体中文", "English"};
        new AlertDialog.Builder(this).setTitle(R.string.language_title)
                .setSingleChoiceItems(names, LanguageChoice.indexOf(AppLocale.selected(this)), (dialog, index) -> {
                    String before = AppLocale.selected(this); AppLocale.select(this, LanguageChoice.TAGS[index]);
                    ScamNotifications.ensureChannel(this); dialog.dismiss();
                    if (!before.equals(LanguageChoice.TAGS[index]) && Build.VERSION.SDK_INT < 33) recreate();
                }).setNegativeButton(R.string.cancel, null).show();
    }
    private void enableMonitoring() {
        List<String> requested = new ArrayList<>();
        if (!has(Manifest.permission.RECEIVE_SMS)) requested.add(Manifest.permission.RECEIVE_SMS);
        if (Build.VERSION.SDK_INT >= 33 && !has(Manifest.permission.POST_NOTIFICATIONS)) requested.add(Manifest.permission.POST_NOTIFICATIONS);
        if (requested.isEmpty()) { AppPreferences.setMonitoring(this, true); updateProtectionStatus(); }
        else requestPermissions(requested.toArray(new String[0]), REQUEST_MONITOR);
    }
    private void requestNotifications() {
        if (Build.VERSION.SDK_INT >= 33 && !has(Manifest.permission.POST_NOTIFICATIONS))
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQUEST_NOTIFICATION);
        else startActivity(new Intent(Settings.ACTION_CHANNEL_NOTIFICATION_SETTINGS)
                .putExtra(Settings.EXTRA_APP_PACKAGE, getPackageName()).putExtra(Settings.EXTRA_CHANNEL_ID, ScamNotifications.CHANNEL));
    }
    private boolean has(String permission) { return checkSelfPermission(permission) == PackageManager.PERMISSION_GRANTED; }
    private void openAppSettings() { startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + getPackageName()))); }
    private void updateProtectionStatus() {
        boolean enabled = AppPreferences.monitoring(this);
        boolean ready = enabled && has(Manifest.permission.RECEIVE_SMS) && ScamNotifications.allowed(this) && !AppPreferences.scannerFailed(this);
        int description = !enabled ? R.string.monitor_off : !has(Manifest.permission.RECEIVE_SMS) ? R.string.monitor_no_sms
                : AppPreferences.scannerFailed(this) ? R.string.monitor_model_error
                : ScamNotifications.allowed(this) ? R.string.monitor_ready : R.string.monitor_no_notifications;
        if (protectionCard != null) {
            protectionCard.setTag(Boolean.valueOf(ready));
            GradientDrawable background = new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                    ready ? new int[]{0xFFDDF6E8, 0xFFE6F5F1} : new int[]{0xFFFBE9E7, 0xFFFFF3EC});
            background.setCornerRadius(dp(26)); protectionCard.setBackground(background);
        }
        if (hero != null) hero.setReady(ready);
        if (protectionTitle != null) { protectionTitle.setText(ready ? R.string.protection_on : R.string.protection_off); protectionTitle.setTextColor(protectionColor(ready)); }
        if (status != null) { status.setText(description); status.setTextColor(ready ? GREEN : RED); }
        setSwitches();
    }
    static int protectionColor(boolean ready) { return ready ? GREEN : RED; }
    private void setSwitches() {
        updatingSwitch = true;
        if (monitor != null) monitor.setChecked(AppPreferences.monitoring(this));
        if (notificationSwitch != null) notificationSwitch.setChecked(AppPreferences.notificationsEnabled(this));
        updatingSwitch = false;
    }

    private void confirmFullScan() {
        if (InboxAccess.progress().running) { toast(R.string.inbox_scan_running); return; }
        new AlertDialog.Builder(this).setTitle(R.string.inbox_all_title).setMessage(R.string.inbox_all_consent)
                .setNegativeButton(R.string.cancel, null).setPositiveButton(R.string.scan, (dialog, which) -> requestInbox(InboxAction.SCAN)).show();
    }
    private void confirmReadInbox() {
        if (inboxConsentAccepted && has(Manifest.permission.READ_SMS)) { showPage(Page.INBOX); loadInboxPage(true); return; }
        new AlertDialog.Builder(this).setTitle(R.string.inbox_read_title).setMessage(R.string.inbox_read_consent)
                .setNegativeButton(R.string.cancel, null).setPositiveButton(R.string.inbox_read_action, (dialog, which) -> requestInbox(InboxAction.READ)).show();
    }
    private void requestInbox(InboxAction action) {
        pendingInboxAction = action;
        if (action == InboxAction.READ) inboxConsentAccepted = true;
        if (has(Manifest.permission.READ_SMS)) performInboxAction();
        else requestPermissions(new String[]{Manifest.permission.READ_SMS}, REQUEST_INBOX);
    }
    private void performInboxAction() {
        InboxAction action = pendingInboxAction; pendingInboxAction = InboxAction.NONE;
        if (action == InboxAction.SCAN) { InboxAccess.startFullScan(this); updateImportProgress(); }
        else if (action == InboxAction.READ) { showPage(Page.INBOX); loadInboxPage(true); }
        refreshData();
    }
    @Override public void onRequestPermissionsResult(int code, String[] permissions, int[] grants) {
        super.onRequestPermissionsResult(code, permissions, grants);
        if (code == REQUEST_MONITOR) {
            AppPreferences.setMonitoring(this, has(Manifest.permission.RECEIVE_SMS));
            if (!has(Manifest.permission.RECEIVE_SMS)) toast(R.string.permission_denied);
        } else if (code == REQUEST_INBOX) {
            if (has(Manifest.permission.READ_SMS)) performInboxAction();
            else { pendingInboxAction = InboxAction.NONE; toast(R.string.inbox_failed); }
        }
        if (currentPage == Page.SETTINGS) showPage(Page.SETTINGS);
        updateProtectionStatus(); refreshData();
    }
    private void loadInboxPage(boolean reset) {
        if (loadingInbox) { if (reset) inboxResetPending = true; return; }
        if (!has(Manifest.permission.READ_SMS)) { requestInbox(InboxAction.READ); return; }
        loadingInbox = true;
        if (reset) { inboxCursors.clear(); inboxBeforeReceived = -1; inboxBeforeId = -1; }
        inboxRows.clear(); inboxLoaded = false; inboxPage = null;
        InboxAccess.Position position = inboxBeforeReceived < 0 ? null : new InboxAccess.Position(inboxBeforeReceived, inboxBeforeId);
        renderInboxRows();
        worker.execute(() -> {
            InboxAccess.InboxPage rows = null;
            try { rows = InboxAccess.readPage(this, position, LIST_PAGE_SIZE); } catch (RuntimeException ignored) {}
            final InboxAccess.InboxPage loaded = rows;
            main.post(() -> {
                if (isDestroyed()) return;
                loadingInbox = false;
                if (inboxResetPending) { inboxResetPending = false; loadInboxPage(true); return; }
                if (loaded == null) toast(R.string.inbox_failed);
                else { inboxPage = loaded; inboxRows.addAll(loaded.records); inboxLoaded = true; }
                renderInboxRows();
            });
        });
    }
    private void nextInboxPage() {
        if (loadingInbox || inboxPage == null || !inboxPage.hasMore || inboxPage.next == null) return;
        inboxCursors.add(new InboxAccess.Position(inboxBeforeReceived, inboxBeforeId));
        inboxBeforeReceived = inboxPage.next.received; inboxBeforeId = inboxPage.next.id;
        loadInboxPage(false); scroll.smoothScrollTo(0, 0);
    }
    private void previousInboxPage() {
        if (loadingInbox || inboxCursors.isEmpty()) return;
        InboxAccess.Position before = inboxCursors.remove(inboxCursors.size() - 1);
        inboxBeforeReceived = before.received; inboxBeforeId = before.id;
        loadInboxPage(false); scroll.smoothScrollTo(0, 0);
    }
    private void renderInboxRows() {
        if (inboxList == null) return;
        inboxList.removeAllViews();
        if (!has(Manifest.permission.READ_SMS)) { inboxRows.clear(); inboxList.addView(note(R.string.daily_received_unavailable)); }
        else if (inboxRows.isEmpty()) inboxList.addView(note(loadingInbox ? R.string.inbox_loading
                : inboxLoaded ? R.string.inbox_empty : R.string.inbox_not_loaded));
        else for (InboxAccess.Sms sms : inboxRows) {
            String sender = sms.sender.isEmpty() ? getString(R.string.unknown_sender) : sms.sender;
            TextView row = recordRow(sender + "\n" + formatDate(sms.received), INK);
            row.setOnClickListener(v -> showInboxMessage(sms)); inboxList.addView(row);
        }
        if (loadMoreButton != null) loadMoreButton.setEnabled(!loadingInbox && inboxPage != null && inboxPage.hasMore);
        if (inboxRefreshButton != null) inboxRefreshButton.setEnabled(!loadingInbox);
        if (inboxPreviousButton != null) inboxPreviousButton.setEnabled(!loadingInbox && !inboxCursors.isEmpty());
        if (inboxPageStatus != null) inboxPageStatus.setText(inboxRows.isEmpty() ? getString(R.string.pagination_empty)
                : getString(R.string.pagination_inbox_page, inboxCursors.size() + 1, inboxRows.size()));
    }
    private void showInboxMessage(InboxAccess.Sms sms) {
        if (!has(Manifest.permission.READ_SMS)) { inboxRows.clear(); renderInboxRows(); toast(R.string.inbox_failed); return; }
        String sender = sms.sender.isEmpty() ? getString(R.string.unknown_sender) : sms.sender;
        showSecure(new AlertDialog.Builder(this).setTitle(R.string.inbox_read_title)
                .setMessage(sender + "\n" + formatDate(sms.received) + "\n\n" + sms.body)
                .setNegativeButton(R.string.close, null)
                .setPositiveButton(R.string.check_this_message, (which, selected) -> queueInboxMessage(sms)).create());
    }
    private void queueInboxMessage(InboxAccess.Sms sms) {
        worker.execute(() -> {
            try {
                MessageStore store = MessageStore.get(this);
                MessageStore.Record existing = store.findExisting(sms.sender, sms.body, sms.received);
                long candidate = existing != null ? existing.id : store.enqueue(sms.sender, sms.body, sms.received, "inbox");
                if (candidate < 0) {
                    existing = store.findExisting(sms.sender, sms.body, sms.received);
                    if (existing != null) candidate = existing.id;
                }
                final long id = candidate;
                if (existing != null && "failed".equals(existing.state)) store.retryFailed(id);
                if (id > 0) ScanScheduler.schedule(this, id);
                main.post(() -> {
                    if (isDestroyed()) return;
                    resultsFilter = ResultFilter.REVIEW; resetResultsPaging(); showPage(Page.RESULTS);
                    pendingDetailsId = id; showPendingDetails(); refreshData();
                });
            } catch (RuntimeException ignored) { main.post(() -> { if (!isDestroyed()) toast(R.string.inbox_failed); }); }
        });
    }
    private void addImportProgress() {
        LinearLayout card = panel(page); importProgressCard = card; card.setVisibility(View.GONE);
        card.addView(text(getString(R.string.scan_progress_title), 16, INK, true));
        progressText = text("", 14, MUTED, false); progressText.setPadding(0, dp(10), 0, dp(10));
        progressText.setId(R.id.scan_progress_text); card.addView(progressText);
        stopButton = secondaryButton(R.string.inbox_stop);
        stopButton.setOnClickListener(v -> { InboxAccess.stopAdding(); updateImportProgress(); }); card.addView(stopButton);
    }
    private void updateImportProgress() {
        if (progressText == null) return;
        InboxAccess.Progress progress = InboxAccess.progress();
        String text = progress.running ? getString(R.string.inbox_queue_running) + "\n" + getString(R.string.inbox_queue_progress, progress.added, progress.existing)
                : progress.failed ? getString(R.string.inbox_queue_failed)
                : progress.stopped ? getString(R.string.inbox_stopped, progress.seen)
                : progress.seen > 0 ? getString(R.string.inbox_scan_summary, progress.added, progress.existing) : "";
        if (statistics != null && (statistics.pending > 0 || statistics.failed > 0))
            text += (text.isEmpty() ? "" : "\n") + getString(R.string.queue_pending_summary, statistics.pending, statistics.failed);
        if (importProgressCard != null) importProgressCard.setVisibility(text.isEmpty() ? View.GONE : View.VISIBLE);
        progressText.setText(text); progressText.setTextColor(progress.failed ? RED : MUTED);
        if (stopButton != null) stopButton.setVisibility(progress.running ? View.VISIBLE : View.GONE);
    }

    private void classifyManual() {
        if (manualBusy || input == null) return;
        String body = input.getText().toString().trim();
        if (body.isEmpty()) { toast(R.string.enter_message); return; }
        if (body.length() > 20000) { toast(R.string.too_long); return; }
        manualBusy = true; lastPrediction = null; lastManualFailed = false; renderManualResult();
        worker.execute(() -> {
            long id = -1;
            try {
                MessageStore store = MessageStore.get(this); id = store.enqueue("", body, System.currentTimeMillis(), "manual");
                LocalMessageClassifier classifier = LocalMessageClassifier.getInstance(this);
                Prediction prediction = classifier.classify(body); if (id > 0) store.complete(id, prediction);
                AppPreferences.setScannerFailed(this, false);
                main.post(() -> {
                    if (isDestroyed()) return;
                    manualBusy = false; lastPrediction = prediction;
                    renderManualResult(); updateProtectionStatus(); refreshData();
                });
            } catch (Exception | LinkageError error) {
                AppPreferences.setScannerFailed(this, true);
                if (id > 0) try { MessageStore.get(this).fail(id); } catch (RuntimeException ignored) {}
                main.post(() -> {
                    if (isDestroyed()) return;
                    manualBusy = false; lastManualFailed = true; renderManualResult(); updateProtectionStatus(); refreshData();
                });
            }
        });
    }
    private void renderManualResult() {
        if (result == null) return;
        checkButton.setEnabled(!manualBusy);
        if (manualBusy) { result.setText(R.string.checking); result.setTextColor(MUTED); }
        else if (lastManualFailed) { result.setText(R.string.scan_failed); result.setTextColor(RED); }
        else if (lastPrediction != null) {
            result.setText(resultText(lastPrediction)); result.setTextColor(resultColor(lastPrediction.isScam, lastPrediction.label, lastPrediction.isUnwanted));
        }
    }
    private void refreshData() {
        if (refreshing || isDestroyed()) return;
        refreshing = true;
        worker.execute(() -> {
            MessageStore.Statistics snapshot = null;
            long received = -1;
            try {
                MessageStore store = MessageStore.get(this); snapshot = store.statistics();
                if (has(Manifest.permission.READ_SMS)) received = InboxAccess.receivedToday(this);
            } catch (RuntimeException ignored) {}
            final MessageStore.Statistics totals = snapshot; final long arrivals = received;
            main.post(() -> {
                refreshing = false;
                if (isDestroyed()) return;
                statistics = totals; inboxReceivedToday = arrivals; renderData(); updateImportProgress();
                if (currentPage == Page.RESULTS) loadResults(false);
            });
        });
    }
    private void renderData() {
        if (receivedCount != null) receivedCount.setText(inboxReceivedToday < 0 ? "—" : number(inboxReceivedToday));
        if (receivedNote != null) receivedNote.setVisibility(inboxReceivedToday < 0 ? View.VISIBLE : View.GONE);
        if (checkedCount != null) checkedCount.setText(statistics == null ? "—" : number(statistics.todayChecked));
        renderResults();
        if (statisticsTable != null) {
            boolean available = statistics != null;
            statisticsTable.setVisibility(available ? View.VISIBLE : View.GONE);
            weeklyTable.setVisibility(available ? View.VISIBLE : View.GONE);
            chart.setVisibility(available ? View.VISIBLE : View.GONE);
            statisticsEmpty.setVisibility(available ? View.GONE : View.VISIBLE);
            legacyNote.setVisibility(available && statistics.legacyChecked > 0 ? View.VISIBLE : View.GONE);
            if (available) {
                setStatisticsRow(R.id.stats_checked_row, statistics.todayChecked, statistics.totalChecked);
                setStatisticsRow(R.id.stats_normal_row, statistics.todayNormal, statistics.totalNormal);
                setStatisticsRow(R.id.stats_spam_row, statistics.todaySpam, statistics.totalSpam);
                setStatisticsRow(R.id.stats_scam_row, statistics.todayScam, statistics.totalScam);
                setStatisticsRow(R.id.stats_review_row, statistics.todayReview, statistics.totalReview);
                setStatisticsRow(R.id.stats_pending_row, null, statistics.pending);
                setStatisticsRow(R.id.stats_failed_row, null, statistics.failed);
                if (statistics.legacyChecked > 0) legacyNote.setText(getString(R.string.stats_legacy, statistics.legacyChecked));
                chart.setDays(statistics.last7Days);
                DateFormat dayFormat = DateFormat.getDateInstance(DateFormat.SHORT, AppLocale.displayLocale(this));
                if (weeklyTable.getChildCount() != statistics.last7Days.size() + 1) {
                    weeklyTable.removeViews(1, weeklyTable.getChildCount() - 1);
                    for (MessageStore.DayStatistics ignored : statistics.last7Days) tableRow(weeklyTable, View.NO_ID, false, "", "");
                }
                for (int i = 0; i < statistics.last7Days.size(); i++) {
                    MessageStore.DayStatistics day = statistics.last7Days.get(i);
                    TableRow row = (TableRow) weeklyTable.getChildAt(i + 1);
                    ((TextView) row.getChildAt(0)).setText(dayFormat.format(new Date(day.startMillis)));
                    ((TextView) row.getChildAt(1)).setText(number(day.checked));
                }
            }
        }
    }
    private TableLayout statisticsTable(LinearLayout parent, int id) {
        HorizontalScrollView viewport = new HorizontalScrollView(this); viewport.setFillViewport(true);
        TableLayout table = new TableLayout(this); table.setId(id); table.setStretchAllColumns(false);
        table.setColumnStretchable(0, true); table.setColumnShrinkable(0, true);
        // Keep counts intact at large font sizes; the entire table can then scroll horizontally.
        table.setMinimumWidth(dp(Math.round(252 * Math.max(1f, getResources().getConfiguration().fontScale))));
        viewport.addView(table, new HorizontalScrollView.LayoutParams(-1, -2));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2); params.topMargin = dp(10);
        parent.addView(viewport, params); return table;
    }
    private void tableHeader(TableLayout table, int id, int... labels) {
        String[] captions = new String[labels.length];
        for (int i = 0; i < labels.length; i++) captions[i] = getString(labels[i]);
        tableRow(table, id, true, captions);
    }
    private TableRow tableRow(TableLayout table, int id, boolean header, String... values) {
        TableRow row = new TableRow(this); row.setId(id); row.setGravity(Gravity.CENTER_VERTICAL);
        row.setBackground(shape(header ? 0xFFE9F4EF : Color.WHITE, BORDER, 0));
        for (int i = 0; i < values.length; i++) {
            TextView cell = text(values[i], header ? 13 : i == 0 ? 14 : 16, header ? TEAL : INK, header);
            cell.setPadding(dp(10), dp(13), dp(10), dp(13));
            cell.setGravity((i == 0 ? Gravity.START : Gravity.END) | Gravity.CENTER_VERTICAL);
            if (i > 0) { cell.setSingleLine(true); cell.setFontFeatureSettings("tnum"); }
            if (header && Build.VERSION.SDK_INT >= 28) cell.setAccessibilityHeading(true);
            row.addView(cell, new TableRow.LayoutParams(-2, -2));
        }
        table.addView(row, new TableLayout.LayoutParams(-1, -2)); return row;
    }
    private void statisticsRow(int id, int label) {
        tableRow(statisticsTable, id, false, getString(label), getString(R.string.count_unknown), getString(R.string.count_unknown));
    }
    private void setStatisticsRow(int id, Long today, long total) {
        TableRow row = statisticsTable.findViewById(id);
        ((TextView) row.getChildAt(1)).setText(today == null ? getString(R.string.count_unknown) : number(today));
        ((TextView) row.getChildAt(2)).setText(number(total));
    }
    private String number(long value) { return NumberFormat.getIntegerInstance(AppLocale.displayLocale(this)).format(value); }
    private String formatDate(long value) { return DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.SHORT, AppLocale.displayLocale(this)).format(new Date(value)); }
    private void showPendingDetails() {
        if (pendingDetailsId <= 0 || isFinishing()) return;
        long id = pendingDetailsId; pendingDetailsId = -1;
        worker.execute(() -> {
            try {
                MessageStore.Record record = MessageStore.get(this).find(id);
                main.post(() -> { if (!isDestroyed() && record != null) showRecord(record); });
            } catch (RuntimeException ignored) {
                main.post(() -> { if (!isDestroyed()) toast(R.string.scan_failed); });
            }
        });
    }
    private void showRecord(MessageStore.Record record) {
        String sender = record.sender.isEmpty() ? getString(R.string.unknown_sender) : record.sender;
        String message = sender + "\n" + formatDate(record.received) + "\n\n" + record.body + "\n\n" + getString(recordCaption(record));
        if ("complete".equals(record.state)) {
            message += "\n" + getString(R.string.probabilities, 100 * record.normal, 100 * record.spam, 100 * record.scam);
            if (record.truncated) message += "\n" + getString(R.string.truncated);
        }
        showSecure(new AlertDialog.Builder(this).setTitle(R.string.details_title)
                .setMessage(message).setPositiveButton(R.string.close, null).create());
    }
    private void showSecure(AlertDialog dialog) {
        if (dialog.getWindow() != null) dialog.getWindow().addFlags(WindowManager.LayoutParams.FLAG_SECURE);
        dialog.show();
        TextView body = dialog.findViewById(android.R.id.message);
        if (body != null) { body.setTextSize(18); body.setAutoLinkMask(0); body.setTextIsSelectable(false); body.setMovementMethod(null); }
    }
    String resultText(Prediction p) {
        int title = p.isScam ? R.string.result_scam : "spam".equals(p.label) ? R.string.result_spam
                : "normal".equals(p.label) && !p.isUnwanted ? R.string.result_normal : R.string.result_review;
        return getString(title) + "\n" + getString(R.string.probabilities, 100 * p.normalProbability, 100 * p.spamProbability, 100 * p.scamProbability)
                + (p.truncated ? "\n" + getString(R.string.truncated) : "");
    }
    private int recordCaption(MessageStore.Record record) {
        if ("pending".equals(record.state)) return R.string.pending;
        if (!"complete".equals(record.state)) return R.string.failed;
        if (!record.decisionMetadataValid) return R.string.result_review;
        return record.isScam ? R.string.result_scam : "spam".equals(record.label) ? R.string.result_spam
                : "normal".equals(record.label) && !record.isUnwanted ? R.string.result_normal : R.string.result_review;
    }
    private int recordColor(MessageStore.Record record) {
        return "pending".equals(record.state) ? MUTED : !"complete".equals(record.state) ? RED
                : !record.decisionMetadataValid ? AMBER : resultColor(record.isScam, record.label, record.isUnwanted);
    }
    static int resultColor(boolean scam, String label, boolean unwanted) { return scam ? RED : "normal".equals(label) && !unwanted ? GREEN : AMBER; }
    private int sourceName(String source) { return "incoming".equals(source) ? R.string.source_incoming : "inbox".equals(source) ? R.string.source_inbox : R.string.source_manual; }

    private LinearLayout column() { LinearLayout view = new LinearLayout(this); view.setOrientation(LinearLayout.VERTICAL); return view; }
    private TextView text(String value, int size, int color, boolean bold) {
        TextView view = new TextView(this); view.setText(value); view.setTextSize(size); view.setTextColor(color);
        view.setTypeface(Typeface.create(bold ? "sans-serif-medium" : "sans-serif", bold ? Typeface.BOLD : Typeface.NORMAL));
        view.setLineSpacing(dp(3), 1); return view;
    }
    private TextView note(int resource) { TextView view = text(getString(resource), 14, MUTED, false); view.setPadding(0, dp(10), 0, dp(10)); return view; }
    private ImageView icon(int drawable, int color, int size) {
        ImageView image = new ImageView(this); image.setImageResource(drawable); image.setImageTintList(ColorStateList.valueOf(color));
        image.setLayoutParams(new LinearLayout.LayoutParams(dp(size), dp(size))); image.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO); return image;
    }
    private LinearLayout panel(LinearLayout parent) {
        LinearLayout card = column(); card.setPadding(dp(18), dp(17), dp(18), dp(17));
        card.setBackground(shape(Color.WHITE, BORDER, 22)); card.setElevation(dp(1));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2); params.topMargin = dp(12); parent.addView(card, params); return card;
    }
    private LinearLayout titledPanel(int title) { LinearLayout card = panel(page); card.addView(text(getString(title), 19, INK, true)); return card; }
    private void pageHeading(int title, int subtitle) {
        pageHeading(title); page.addView(note(subtitle));
    }
    private void pageHeading(int title) {
        TextView heading = text(getString(title), 29, INK, true); heading.setPadding(0, dp(7), 0, dp(2)); page.addView(heading);
    }
    private void sectionTitle(int title) { TextView heading = text(getString(title), 18, INK, true); heading.setPadding(0, dp(22), 0, 0); page.addView(heading); }
    private TextView metricCell(LinearLayout parent, int label) {
        LinearLayout cell = column(); cell.setPadding(dp(5), 0, dp(5), 0); cell.setGravity(Gravity.CENTER);
        TextView number = text("—", 32, INK, true); number.setGravity(Gravity.CENTER); cell.addView(number);
        TextView caption = text(getString(label), 14, MUTED, false); caption.setGravity(Gravity.CENTER); cell.addView(caption);
        parent.addView(cell, new LinearLayout.LayoutParams(0, -2, 1)); return number;
    }
    private LinearLayout actionCard(int id, int drawable, int title, int description, Runnable click) {
        LinearLayout card = column(); card.setId(id); card.setMinimumHeight(dp(92));
        card.setPadding(dp(16), dp(16), dp(16), dp(16)); card.setBackground(clickableBackground(Color.WHITE, BORDER, 20));
        card.addView(icon(drawable, TEAL, 27));
        TextView heading = text(getString(title), 17, INK, true); heading.setPadding(0, dp(11), 0, dp(3)); card.addView(heading);
        card.addView(text(getString(description), 13, MUTED, false));
        card.setFocusable(true); card.setContentDescription(getString(title) + ". " + getString(description)); card.setOnClickListener(v -> click.run());
        return card;
    }
    private void action(LinearLayout parent, boolean stacked, int id, int drawable, int title, int description, Runnable click) {
        LinearLayout card = actionCard(id, drawable, title, description, click);
        LinearLayout.LayoutParams params = stacked ? new LinearLayout.LayoutParams(-1, -2) : new LinearLayout.LayoutParams(0, -2, 1);
        params.topMargin = dp(10); if (!stacked && parent.getChildCount() > 0) params.leftMargin = dp(10); parent.addView(card, params);
    }
    private Button primaryButton(int label) { return button(label, true); }
    private Button secondaryButton(int label) { return button(label, false); }
    private Button button(int label, boolean filled) {
        Button button = new Button(this); button.setText(label); button.setTextSize(16); button.setAllCaps(false);
        button.setTextColor(new ColorStateList(new int[][]{new int[]{-android.R.attr.state_enabled}, new int[]{}},
                new int[]{filled ? 0xFFADC7BD : 0xFF91A79E, filled ? Color.WHITE : TEAL}));
        button.setMinimumHeight(dp(54)); button.setPadding(dp(14), dp(10), dp(14), dp(10));
        button.setBackground(clickableBackground(filled ? TEAL : 0xFFF3F9F6, filled ? TEAL : BORDER, 15));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2); params.topMargin = dp(10); button.setLayoutParams(params); return button;
    }
    private Switch toggle(LinearLayout parent, int id, int label) {
        Switch view = new Switch(this); view.setId(id); view.setText(label); view.setTextSize(17); view.setTextColor(INK);
        view.setMinimumHeight(dp(62)); view.setPadding(0, dp(10), 0, dp(10)); view.setSwitchPadding(dp(15));
        parent.addView(view, new LinearLayout.LayoutParams(-1, -2)); return view;
    }
    private TextView recordRow(String caption, int color) {
        TextView row = text(caption, 16, color, false); row.setPadding(dp(13), dp(15), dp(13), dp(15)); row.setMinHeight(dp(72));
        row.setBackground(clickableBackground(0xFFF7FAF8, BORDER, 14));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2); params.topMargin = dp(9); row.setLayoutParams(params);
        row.setFocusable(true); row.setClickable(true); return row;
    }
    private GradientDrawable shape(int fill, int border, int radius) {
        GradientDrawable drawable = new GradientDrawable(); drawable.setColor(fill); drawable.setCornerRadius(dp(radius));
        if (border != Color.TRANSPARENT) drawable.setStroke(dp(1), border); return drawable;
    }
    private RippleDrawable clickableBackground(int fill, int border, int radius) {
        return new RippleDrawable(ColorStateList.valueOf(0x22137C6B), shape(fill, border, radius), shape(Color.WHITE, Color.TRANSPARENT, radius));
    }
    private int dp(int value) { return Math.round(getResources().getDisplayMetrics().density * value); }
    private void toast(int message) { Toast.makeText(this, message, Toast.LENGTH_LONG).show(); }
}
