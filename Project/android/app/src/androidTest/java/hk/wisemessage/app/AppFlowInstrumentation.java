package hk.wisemessage.app;

import android.Manifest;
import android.app.Activity;
import android.app.Instrumentation;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.ActivityInfo;
import android.content.pm.ServiceInfo;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.TimeZone;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import org.json.JSONArray;
import org.json.JSONObject;
import hk.wisemessage.app.ml.LocalMessageClassifier;
import hk.wisemessage.app.ml.Prediction;
import hk.wisemessage.app.ml.WordPieceTokenizer;

/** Device-only integration checks. No cloud calls, SMS sending, or SMS inbox permission grants. */
public final class AppFlowInstrumentation extends Instrumentation {
    @Override public void onCreate(Bundle arguments) { super.onCreate(arguments); start(); }
    @Override public void onStart() {
        Bundle results=new Bundle(); long started=System.currentTimeMillis(); int passed=0;
        try {
            verifyManifest(); passed++;
            verifyLanguages(); passed++;
            LocalMessageClassifier classifier=LocalMessageClassifier.getInstance(getTargetContext());
            Prediction traditional=classifier.classify("明天下午三點有牙科預約，請攜帶身份證。 ");
            Prediction simplified=classifier.classify("明天下午三点有牙科预约，请携带身份证。");
            verifyPrediction(traditional); verifyPrediction(simplified); passed++;
            String parityReport=verifyFixtureParity(classifier,results); passed++;
            verifyPrivateStore(traditional); passed++;
            verifyPreservingMigration(); passed++;
            verifyDashboardNavigation(); passed++;
            verifyResultsNavigation(); passed++;
            verifyManualScreen(); passed++;
            results.putString("stream","WiseMessage offline integration: "+passed+" checks passed. "+parityReport+" "
                    +"SMS receipt, installer restrictions, notification visibility, and Samsung battery behavior require the physical-phone checklist.\n");
            results.putInt("tests_passed",passed); results.putLong("elapsed_ms",System.currentTimeMillis()-started);
            finish(Activity.RESULT_OK,results);
        } catch (Throwable error) {
            results.putString("stream","Offline integration failed after "+passed+" checks: "+error.getClass().getSimpleName()+": "+error.getMessage()+"\n");
            results.putString("failure",error.toString()); results.putInt("tests_passed",passed);
            finish(Activity.RESULT_CANCELED,results);
        }
    }
    private void verifyManifest() throws Exception {
        PackageInfo info=getTargetContext().getPackageManager().getPackageInfo(getTargetContext().getPackageName(),
                PackageManager.GET_PERMISSIONS|PackageManager.GET_RECEIVERS|PackageManager.GET_SERVICES);
        check(info.requestedPermissions!=null,"Missing permission declarations");
        check(!Arrays.asList(info.requestedPermissions).contains(Manifest.permission.INTERNET),"App must not have INTERNET permission");
        check(!Arrays.asList(info.requestedPermissions).contains(Manifest.permission.SEND_SMS),"App must not send SMS");
        check((info.applicationInfo.flags & android.content.pm.ApplicationInfo.FLAG_ALLOW_BACKUP)==0,"SMS records must not be cloud-backed-up");
        boolean receiver=false,job=false;
        for (ActivityInfo component:info.receivers) if (component.name.endsWith(".SmsReceiver")) {
            receiver=true; check(Manifest.permission.BROADCAST_SMS.equals(component.permission),"Receiver must reject untrusted SMS injection");
        }
        for (ServiceInfo component:info.services) if (component.name.endsWith(".MessageScanJobService")) {
            job=true; check("android.permission.BIND_JOB_SERVICE".equals(component.permission),"Job service must require system binding");
        }
        check(receiver&&job,"Incoming SMS processing components are missing");
    }
    private void verifyLanguages() {
        android.content.Context context=getTargetContext();
        String before=AppLocale.selected(context);
        String[] tags={"zh-Hant","zh-Hans","en"};
        String[] expected={"疑似詐騙 · 請先核實","疑似诈骗 · 请先核实","Possible scam · Verify first"};
        String[] resultsTitles={"偵測結果","检测结果","Detection results"};
        try {
            for (int i=0;i<tags.length;i++) {
                AppLocale.select(context,tags[i]);
                android.content.Context localized=AppLocale.wrap(context);
                check(tags[i].equals(AppLocale.selected(context)),"App language was not persisted: "+tags[i]);
                check(expected[i].equals(localized.getString(R.string.result_scam)),"Wrong result translation: "+tags[i]);
                check(resultsTitles[i].equals(localized.getString(R.string.detection_results_title)),"Wrong results navigation translation: "+tags[i]);
                check(localized.getString(R.string.inbox_page_note).contains("20"),"Inbox page size translation must match implementation: "+tags[i]);
                check(localized.getString(R.string.results_page_note).contains("20"),"Result page size translation must match implementation: "+tags[i]);
                check(!localized.getString(R.string.filter_review).isEmpty(),"Missing review filter translation: "+tags[i]);
                check(!localized.getString(R.string.notification_title).isEmpty(),"Missing warning translation: "+tags[i]);
                check(localized.getString(R.string.probabilities,10.,20.,70.).contains("70"),"Invalid localized score format: "+tags[i]);
                ScamNotifications.ensureChannel(context);
                android.app.NotificationChannel channel=context.getSystemService(android.app.NotificationManager.class).getNotificationChannel(ScamNotifications.CHANNEL);
                check(localized.getString(R.string.notification_channel).contentEquals(channel.getName()),"Background notification channel uses wrong language: "+tags[i]);
            }
        } finally {
            AppLocale.select(context,before);
            ScamNotifications.ensureChannel(context);
        }
    }
    private void verifyPrediction(Prediction p) {
        check(Arrays.asList("normal","spam","scam").contains(p.label),"Invalid classifier label");
        double sum=p.normalProbability+p.spamProbability+p.scamProbability;
        check(Double.isFinite(sum)&&Math.abs(sum-1)<0.0001,"Probabilities must sum to one");
        check(p.normalProbability>=0&&p.spamProbability>=0&&p.scamProbability>=0,"Negative probability");
        check(p.isScam=="scam".equals(p.label),"Scam alert must match the exported model decision");
        check(p.inferenceMillis>=0,"Invalid inference time");
    }
    private String verifyFixtureParity(LocalMessageClassifier classifier,Bundle results) throws Exception {
        JSONArray cases;
        try (InputStream stream=getTargetContext().getAssets().open("wisemessage/parity_cases.json");
             ByteArrayOutputStream bytes=new ByteArrayOutputStream()) {
            byte[] buffer=new byte[8192]; int read;
            while ((read=stream.read(buffer))!=-1) {
                check(bytes.size()+read<=2*1024*1024,"Unexpectedly large parity fixture"); bytes.write(buffer,0,read);
            }
            cases=new JSONArray(new String(bytes.toByteArray(),StandardCharsets.UTF_8));
        }
        check(cases.length()==120,"Expected all 120 tokenizer parity cases");
        WordPieceTokenizer tokenizer;
        try (InputStreamReader vocabulary=new InputStreamReader(getTargetContext().getAssets().open("wisemessage/vocab.txt"),StandardCharsets.UTF_8)) {
            tokenizer=new WordPieceTokenizer(vocabulary,256);
        }
        int modelCases=0; long elapsed=0; double maximumError=0;
        String[] labels={"normal","spam","scam"};
        for (int index=0;index<cases.length();index++) {
            JSONObject fixture=cases.getJSONObject(index); String id=fixture.getString("id");
            WordPieceTokenizer.Encoding encoded=tokenizer.encode(fixture.getString("text"));
            check(Arrays.equals(encoded.inputIds,integerArray(fixture.getJSONArray("input_ids"))),"Token IDs differ for "+id);
            check(Arrays.equals(encoded.attentionMask,integerArray(fixture.getJSONArray("attention_mask"))),"Attention mask differs for "+id);
            check(Arrays.equals(encoded.tokenTypeIds,integerArray(fixture.getJSONArray("token_type_ids"))),"Token types differ for "+id);
            if (!fixture.has("probabilities")) continue;
            JSONArray expected=fixture.getJSONArray("probabilities"); check(expected.length()==3,"Invalid probability fixture "+id);
            Prediction actual=classifier.classify(fixture.getString("text")); verifyPrediction(actual);
            double[] scores={actual.normalProbability,actual.spamProbability,actual.scamProbability}; int selected=0;
            for (int label=0;label<3;label++) {
                double error=Math.abs(scores[label]-expected.getDouble(label)); maximumError=Math.max(maximumError,error);
                check(error<=0.001,"ARM64 model probability differs by more than 0.001 for "+id);
                if (expected.getDouble(label)>expected.getDouble(selected)) selected=label;
            }
            check(labels[selected].equals(actual.label),"ARM64 predicted label differs for "+id);
            elapsed+=actual.inferenceMillis; modelCases++;
        }
        check(modelCases==96,"Expected all 96 model-probability parity cases");
        double mean=(double)elapsed/modelCases;
        results.putInt("parity_tokenizer_cases",cases.length()); results.putInt("parity_model_cases",modelCases);
        results.putDouble("parity_max_probability_error",maximumError); results.putDouble("parity_mean_inference_ms",mean);
        return String.format(java.util.Locale.ROOT,"Device parity: %d tokenizer and %d model cases; max probability error %.8f; mean warm inference %.2f ms.",
                cases.length(),modelCases,maximumError,mean);
    }
    private static int[] integerArray(JSONArray values) throws Exception {
        int[] result=new int[values.length()]; for (int i=0;i<result.length;i++) result[i]=values.getInt(i); return result;
    }
    private void verifyPrivateStore(Prediction p) {
        MessageStore store=MessageStore.get(getTargetContext()); long timestamp=System.currentTimeMillis();
        MessageStore.Statistics before=store.statistics(timestamp,TimeZone.getDefault());
        String body="[WiseMessage instrumentation test] 明天開會。";
        long id=store.enqueue("local-test",body,timestamp,"manual"); check(id>0,"Failed to persist queued message");
        check(store.enqueue("local-test",body,timestamp,"inbox")==-1,"Duplicate incoming/inbox message must be deduplicated");
        check("pending".equals(store.find(id).state),"Initial message state must be pending");
        check(store.complete(id,p),"Failed to persist classification");
        check(!store.complete(id,p),"Duplicate job must not complete or notify twice");
        MessageStore.Record record=store.find(id);
        check(body.equals(record.body)&&"complete".equals(record.state),"Stored message/result changed unexpectedly");
        check(record.isScam==p.isScam,"Stored warning decision changed");
        check(record.completedAt>=timestamp,"New checks must record their actual completion timestamp");
        MessageStore.Statistics after=store.statistics(timestamp,TimeZone.getDefault());
        check(after.totalReceived==before.totalReceived,"Manual checks must not count as received SMS");
        check(after.totalChecked==before.totalChecked+1,"One completed manual check must increment the checked total once");
        check(after.todayChecked==before.todayChecked+1,"A completed manual check must count on the completion day");
        long yesterday=StatisticsWindow.day(timestamp,TimeZone.getDefault(),-1).startMillis+1000;
        long oldId=store.enqueue("local-test","[WiseMessage instrumentation test] Historical inbox message. "+timestamp,yesterday,"inbox");
        check(oldId>0&&store.complete(oldId,p),"Failed to classify the historical inbox fixture");
        MessageStore.Statistics historical=store.statistics(timestamp,TimeZone.getDefault());
        check(historical.totalReceived==after.totalReceived+1,"An inbox SMS must count as a received SMS");
        check(historical.todayReceived==after.todayReceived,"Yesterday's SMS must not be counted as received today");
        check(historical.todayChecked==after.todayChecked+1,"An old SMS checked today must count as checked today");
        check(historical.last7Days.size()==7,"Statistics must include seven local calendar days");
        Prediction uncertain=Prediction.fromLogits(new float[]{(float)Math.log(.4),(float)Math.log(.3),(float)Math.log(.3)},.5,false,0);
        long reviewId=store.enqueue("","[WiseMessage instrumentation test] Ambiguous review fixture. "+timestamp,timestamp,"manual");
        check(reviewId>0&&store.complete(reviewId,uncertain),"Failed to save an ambiguous prediction");
        MessageStore.Statistics review=store.statistics(timestamp,TimeZone.getDefault());
        check(review.todayReview==historical.todayReview+1&&review.totalReview==historical.totalReview+1,
                "Ambiguous unwanted predictions must count as needing review");
        check(review.todayNormal==historical.todayNormal&&review.totalNormal==historical.totalNormal,
                "Ambiguous unwanted predictions must not count as reassuring normal results");
        check(review.todayChecked==review.todayNormal+review.todayReview+review.todaySpam+review.todayScam,
                "Today's result categories must partition completed checks");
        String retryBody="[WiseMessage instrumentation test] Retry preserves the original message. "+timestamp;
        long retryId=store.enqueue("local-test",retryBody,timestamp,"inbox");
        check(retryId>0,"Failed to enqueue the retry fixture");
        store.fail(retryId); check("failed".equals(store.find(retryId).state),"Failed fixture must be marked failed");
        check(store.retryFailed(retryId),"Explicit retry must return a failed record to pending");
        MessageStore.Record retry=store.find(retryId);
        check(retry.id==retryId&&retryBody.equals(retry.body)&&"local-test".equals(retry.sender)
                &&retry.received==timestamp&&"inbox".equals(retry.source)&&"pending".equals(retry.state),
                "Retry must preserve the same record, contents and receipt timestamp");
        check(!store.retryFailed(retryId),"Retry must not modify a record that is already pending");
        check(store.complete(retryId,p),"Retried fixture must complete successfully");
        MessageStore.Record completedRetry=store.find(retryId);
        check(!store.retryFailed(retryId),"Retry must never reset a completed prediction");
        MessageStore.Record unchangedRetry=store.find(retryId);
        check("complete".equals(unchangedRetry.state)&&unchangedRetry.completedAt==completedRetry.completedAt
                &&unchangedRetry.label.equals(completedRetry.label)&&retryBody.equals(unchangedRetry.body),
                "Retrying a completed result must leave its date, prediction and contents unchanged");
        // Test rows are intentionally preserved; this test never deletes files or SMS messages.
    }
    private void verifyPreservingMigration() {
        // An in-memory copy tests the old schema without changing or clearing any installed history.
        try (SQLiteDatabase old=SQLiteDatabase.create(null)) {
            old.execSQL("CREATE TABLE messages (_id INTEGER PRIMARY KEY, body TEXT, received INTEGER, state TEXT)");
            old.execSQL("INSERT INTO messages (_id,body,received,state) VALUES (1,'preserved fixture',123,'complete')");
            MessageStore.get(getTargetContext()).onUpgrade(old,1,2);
            try (Cursor row=old.rawQuery("SELECT body,received,state,completed_at FROM messages WHERE _id=1",null)) {
                check(row.moveToFirst(),"Schema upgrade removed an existing record");
                check("preserved fixture".equals(row.getString(0))&&row.getLong(1)==123&&"complete".equals(row.getString(2)),
                        "Schema upgrade changed existing contents or predictions");
                check(row.isNull(3),"Legacy completion dates must remain unknown rather than fabricated");
                check(!row.moveToNext(),"Schema upgrade duplicated an existing record");
            }
        }
    }
    private void verifyDashboardNavigation() throws Exception {
        boolean monitoringBefore=AppPreferences.monitoring(getTargetContext());
        boolean notificationsBefore=AppPreferences.notificationsEnabled(getTargetContext());
        AppPreferences.setMonitoring(getTargetContext(),false);
        MainActivity screen=(MainActivity)startActivitySync(new Intent(getTargetContext(),MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
        try {
            waitForIdleSync();
            runOnMainSync(() -> {
                requireVisible(screen,R.id.home_screen,"Home must be the initial destination");
                requireVisible(screen,R.id.daily_received_count,"Home is missing today's received counter");
                requireVisible(screen,R.id.daily_checked_count,"Home is missing today's checked counter");
                requireVisible(screen,R.id.scan_all_button,"Home is missing the global inbox scan action");
                check(MainActivity.protectionColor(true)!=MainActivity.protectionColor(false),"Complete and incomplete protection need distinct colors");
                check(Boolean.FALSE.equals(screen.findViewById(R.id.protection_card).getTag()),"Monitoring off must never show complete protection");
                click(screen,R.id.nav_messages); requireVisible(screen,R.id.messages_screen,"Messages navigation failed");
                requireVisible(screen,R.id.inbox_entry_button,"Messages must have an inbox entry");
                requireVisible(screen,R.id.results_entry_button,"Messages must have a separate results entry");
                check(screen.findViewById(R.id.history_container)==null,"Messages hub must not embed the long result list");
                check(screen.findViewById(R.id.inbox_container)==null,"Messages hub must not embed the inbox list");
                click(screen,R.id.nav_statistics); requireVisible(screen,R.id.statistics_screen,"Statistics navigation failed");
                click(screen,R.id.nav_settings); requireVisible(screen,R.id.settings_screen,"Settings navigation failed");
                requireVisible(screen,R.id.language_button,"Settings must provide language selection");
                requireVisible(screen,R.id.grant_sms_button,"Settings must expose SMS permission management");
                requireVisible(screen,R.id.grant_inbox_button,"Settings must expose inbox permission management");
                requireVisible(screen,R.id.notification_test_button,"Settings must provide notification testing");
                Switch alerts=screen.findViewById(R.id.notification_switch);
                if (alerts.isChecked()) alerts.performClick();
                check(!AppPreferences.notificationsEnabled(getTargetContext()),"Disabling warnings was not persisted");
                check(!ScamNotifications.allowed(getTargetContext()),"App notification opt-out must suppress warning notifications");
                click(screen,R.id.nav_home);
                check(Boolean.FALSE.equals(screen.findViewById(R.id.protection_card).getTag()),"Missing alerts must not show complete protection");
                click(screen,R.id.manual_nav_button); requireVisible(screen,R.id.manual_screen,"Manual-check navigation failed");
                requireVisible(screen,R.id.manual_input,"Manual input is missing");
                requireVisible(screen,R.id.classify_button,"Manual model action is missing");
                click(screen,R.id.nav_home); requireVisible(screen,R.id.home_screen,"Return to dashboard failed");
            });
        } finally {
            AppPreferences.setMonitoring(getTargetContext(),monitoringBefore);
            AppPreferences.setNotificationsEnabled(getTargetContext(),notificationsBefore);
            runOnMainSync(screen::finish);
        }
    }
    private static void requireVisible(Activity screen,int id,String message) {
        View view=screen.findViewById(id); check(view!=null&&view.isShown(),message);
    }
    private static void click(Activity screen,int id) {
        View view=screen.findViewById(id); check(view!=null,"Missing navigation action: "+id);
        check(view.performClick(),"Navigation action did not handle its click: "+id);
    }
    private void verifyResultsNavigation() throws Exception {
        // All fixtures are completed directly in the debug application's private
        // database: no SMS provider writes, user grants, alerts or file deletion.
        MessageStore store=MessageStore.get(getTargetContext());
        long timestamp=System.currentTimeMillis();
        Prediction spam=Prediction.fromLogits(new float[]{-5,5,-5},.5,false,0);
        Prediction scam=Prediction.fromLogits(new float[]{-5,-5,5},.5,false,0);
        Prediction normal=Prediction.fromLogits(new float[]{5,-5,-5},.5,false,0);
        Prediction review=Prediction.fromLogits(new float[]{(float)Math.log(.4),(float)Math.log(.3),(float)Math.log(.3)},.5,false,0);
        for (int i=0;i<64;i++) {
            String body="[WiseMessage pagination fixture] "+timestamp+" / "+i;
            long id=store.enqueue("local-pagination",body,timestamp+i,"manual");
            Prediction prediction=i<58?(i%2==0?spam:scam):i<61?normal:review;
            check(id>0&&store.complete(id,prediction),"Failed to save a non-destructive pagination fixture");
        }
        long invalidId=store.enqueue("local-pagination","[WiseMessage missing metadata fixture] "+timestamp,timestamp+65,"manual");
        check(invalidId>0&&store.complete(invalidId,normal),"Failed to save the missing-metadata fixture");
        store.getWritableDatabase().execSQL("UPDATE messages SET is_unwanted=NULL WHERE _id=?",new Object[]{invalidId});
        check(!store.find(invalidId).decisionMetadataValid,"Missing decision metadata must be marked for review");
        MainActivity screen=(MainActivity)startActivitySync(new Intent(getTargetContext(),MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
        try {
            waitForIdleSync();
            runOnMainSync(() -> {
                click(screen,R.id.nav_messages);
                click(screen,R.id.results_entry_button);
                requireVisible(screen,R.id.results_screen,"Results entry must open its own destination");
                Spinner filter=screen.findViewById(R.id.results_filter);
                check(filter.getCount()==4,"Results must expose four categories");
                check(filter.getSelectedItemPosition()==0,"Harmful must be the initial results category");
                requireVisible(screen,R.id.results_refresh_button,"Results must expose an explicit refresh action");
            });
            awaitResultRows(screen,0,20);
            List<Long> first=visibleResultIds(screen);
            runOnMainSync(() -> {
                check(!screen.findViewById(R.id.results_previous_button).isEnabled(),"Previous must be disabled on the first results page");
                check(screen.findViewById(R.id.results_next_button).isEnabled(),"More than 20 harmful fixtures must offer a next page");
                click(screen,R.id.results_next_button);
            });
            awaitNewPage(screen,first,0);
            List<Long> second=visibleResultIds(screen);
            check(disjoint(first,second),"Next must replace the result page, not repeat or append its rows");
            runOnMainSync(() -> {
                Bundle state=new Bundle(); screen.onSaveInstanceState(state);
                check("RESULTS".equals(state.getString("page")),"Saved navigation must retain the result destination");
                check("HARMFUL".equals(state.getString("results_filter")),"Saved navigation must retain the selected filter");
                check(state.getLong("results_before",0)>0,"Saved result position must contain the metadata cursor");
                long[] cursors=state.getLongArray("result_cursors");
                check(cursors!=null&&cursors.length==1,"Saved navigation must preserve its previous-page cursor stack");
            });
            runOnMainSync(() -> click(screen,R.id.results_next_button));
            awaitNewPage(screen,second,0);
            List<Long> third=visibleResultIds(screen);
            check(disjoint(first,third)&&disjoint(second,third),"Third results page repeated an earlier record");
            runOnMainSync(() -> click(screen,R.id.results_previous_button));
            awaitResultIds(screen,second);
            for (int category=1;category<=3;category++) {
                final int selected=category;
                runOnMainSync(() -> ((Spinner)screen.findViewById(R.id.results_filter)).setSelection(selected));
                awaitResultRows(screen,category,category==3?20:3);
                runOnMainSync(() -> check(!screen.findViewById(R.id.results_previous_button).isEnabled(),"Changing the category must return to its first page"));
            }
            runOnMainSync(() -> ((Spinner)screen.findViewById(R.id.results_filter)).setSelection(0));
            awaitResultIds(screen,first);
            runOnMainSync(() -> click(screen,R.id.results_next_button));
            awaitResultIds(screen,second);
            runOnMainSync(() -> click(screen,R.id.results_refresh_button));
            awaitResultIds(screen,first);
            runOnMainSync(() -> {
                click(screen,R.id.nav_messages);
                requireVisible(screen,R.id.messages_screen,"Results must return to the short Messages hub");
                check(screen.findViewById(R.id.history_container)==null,"Returning to Messages must remove the result rows");
            });
        } finally { runOnMainSync(screen::finish); }
    }
    private static boolean matchesCategory(MessageStore.Record record,int category) {
        boolean harmful="complete".equals(record.state)&&("spam".equals(record.label)||"scam".equals(record.label)||record.isScam);
        boolean normal="complete".equals(record.state)&&"normal".equals(record.label)&&!record.isScam&&!record.isUnwanted&&record.decisionMetadataValid;
        return category==3||category==0&&harmful||category==1&&normal||category==2&&!harmful&&!normal;
    }
    private List<Long> visibleResultIds(MainActivity screen) {
        List<Long> ids=new ArrayList<>();
        runOnMainSync(() -> {
            LinearLayout rows=screen.findViewById(R.id.history_container);
            check(rows!=null&&rows.getChildCount()<=20,"Results must remain bounded to 20 displayed rows");
            for(int i=0;i<rows.getChildCount();i++) {
                Object tag=rows.getChildAt(i).getTag();
                if(tag instanceof MessageStore.Record) ids.add(((MessageStore.Record)tag).id);
            }
        });
        check(ids.size()==new HashSet<>(ids).size(),"One page must not show duplicate records");
        return ids;
    }
    private void awaitResultRows(MainActivity screen,int category,int minimum) throws Exception {
        long deadline=System.currentTimeMillis()+15000;
        while(System.currentTimeMillis()<deadline) {
            boolean[] ready={false};
            runOnMainSync(() -> {
                LinearLayout rows=screen.findViewById(R.id.history_container);
                if(rows==null) return;
                check(rows.getChildCount()<=20,"Filtering must replace the current page, never accumulate rows");
                int matches=0,recordCount=0;
                for(int i=0;i<rows.getChildCount();i++) {
                    Object tag=rows.getChildAt(i).getTag();
                    if(tag instanceof MessageStore.Record) {
                        recordCount++; if(matchesCategory((MessageStore.Record)tag,category)) matches++;
                    }
                }
                ready[0]=recordCount>=minimum&&matches==recordCount;
            });
            if(ready[0]) return;
            Thread.sleep(50);
        }
        throw new AssertionError("Timed out waiting for the bounded results category "+category);
    }
    private void awaitNewPage(MainActivity screen,List<Long> previous,int category) throws Exception {
        long deadline=System.currentTimeMillis()+15000;
        while(System.currentTimeMillis()<deadline) {
            List<Long> current=visibleResultIds(screen);
            if(!current.isEmpty()&&!current.equals(previous)) { awaitResultRows(screen,category,1); return; }
            Thread.sleep(50);
        }
        throw new AssertionError("Next did not replace the current result page");
    }
    private void awaitResultIds(MainActivity screen,List<Long> expected) throws Exception {
        long deadline=System.currentTimeMillis()+15000;
        while(System.currentTimeMillis()<deadline) {
            if(visibleResultIds(screen).equals(expected)) return;
            Thread.sleep(50);
        }
        throw new AssertionError("The selected result page did not restore its prior records");
    }
    private static boolean disjoint(List<Long> first,List<Long> second) {
        Set<Long> overlap=new HashSet<>(first); overlap.retainAll(second); return overlap.isEmpty();
    }
    private void verifyManualScreen() throws Exception {
        Intent open=new Intent(getTargetContext(),MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        MainActivity screen=(MainActivity)startActivitySync(open); waitForIdleSync();
        runOnMainSync(() -> click(screen,R.id.manual_nav_button)); waitForIdleSync();
        // A normal argmax can coexist with a majority combined unwanted score.
        // Preserve that ambiguity in the UI instead of displaying a reassuring green result.
        Prediction uncertain=Prediction.fromLogits(new float[]{(float)Math.log(.4),(float)Math.log(.3),(float)Math.log(.3)},.5,false,0);
        check("normal".equals(uncertain.label)&&uncertain.isUnwanted,"Invalid ambiguous UI fixture");
        check(screen.resultText(uncertain).contains(AppLocale.wrap(getTargetContext()).getString(R.string.result_review)),"Ambiguous unwanted result must request review");
        check(MainActivity.resultColor(false,"normal",true)!=MainActivity.resultColor(false,"normal",false),"Ambiguous unwanted result must not use normal green");
        check(MainActivity.resultColor(false,"spam",true)==MainActivity.resultColor(false,"normal",true),"Spam and uncertain results should use review amber");
        runOnMainSync(() -> {
            ((EditText)screen.findViewById(R.id.manual_input)).setText("明天下午三點有牙科預約，請攜帶身份證。");
            ((Button)screen.findViewById(R.id.classify_button)).performClick();
        });
        long deadline=System.currentTimeMillis()+60000; final boolean[] finished={false}; final String[] content={""};
        while (System.currentTimeMillis()<deadline) {
            runOnMainSync(() -> {
                finished[0]=screen.findViewById(R.id.classify_button).isEnabled();
                content[0]=((TextView)screen.findViewById(R.id.result_text)).getText().toString();
            });
            if (finished[0]) break;
            Thread.sleep(100);
        }
        check(finished[0],"Manual model inference timed out");
        check(!content[0].isEmpty()&&!content[0].equals(getTargetContext().getString(R.string.scan_failed)),"Manual model inference failed");
        check(content[0].contains("%"),"Manual screen did not display model probabilities");
        runOnMainSync(screen::finish);
    }
    private static void check(boolean condition,String message) { if (!condition) throw new AssertionError(message); }
}
