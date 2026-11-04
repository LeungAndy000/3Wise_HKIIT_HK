# WiseMessage 3.1: separate inbox and detection results

Version 3.0 was confirmed working on a test phone. That observation
does not establish that version 3.1 has passed physical-phone testing.
Host compilation, resource audits and JVM/SQL tests must be recorded separately
from Android instrumentation and the following phone checks.

## Update without losing records

Install the signed version 3.1 update over the current application. Do not
uninstall, clear application data, clear the SMS inbox or reset Android settings.
Verify that existing records, language, protection preference and warning
preference remain available. The classifier, thresholds and notification policy
are unchanged in this release. No OCR is integrated by this list-navigation
update.

## Navigation and bounded lists

Repeat in Traditional Chinese, Simplified Chinese and English, including a
narrow screen and 200% system font size:

1. Open **Messages**. Confirm it is a short navigation page with separate
   **Read phone SMS** and **Detection results** entries, rather than two long
   lists. Home's read-SMS shortcut should open the inbox flow.
2. Open **Read phone SMS**, approve its disclosure and grant inbox access if
   desired. With more than 60 accessible synthetic SMS, advance four pages
   and return with Previous. At most 20 rows are visible on each page; changing
   pages replaces rows rather than appending them. Refresh returns to the first
   page. Message text stays hidden until a secure detail dialog is opened.
3. Revoke READ_SMS in Android settings and return to the inbox. No previously
   loaded sender, body or message detail should remain visible. Show the access
   explanation. Denial must not change existing private analysis records.
4. Open **Detection results**. The default category is **Harmful · possible spam
   or scam**. At most 20 results are visible per page. Advance and return across
   several pages; no rows should be appended into a long cumulative list.
5. Change each filter. Every change starts at the first page of that category.
   Confirm the displayed range and matching total, first-page Previous state,
   final-page Next state, empty-category explanation and refresh behavior.
6. Rotate while viewing a later result page and after choosing a different
   category. The selected category and navigation position should restore from
   metadata. Saved Android state must never contain SMS bodies or manual text.
7. Return to Messages and then Home. Confirm the lists are not embedded in the
   navigation hub and that incoming checks continue unchanged in the background.

## Correct category semantics

Check categories against synthetic records with known persisted states:

| Filter | Records expected |
|---|---|
| Harmful · possible spam or scam | Completed spam or scam decisions |
| No high risk detected | Completed normal decision without the combined unwanted-review flag |
| Review or unfinished | Uncertain decisions, waiting checks, failed checks, or unrecognised/incomplete metadata |
| All results | Every stored record, including pending and failed checks |

These are model decisions, not proof that a message is legitimate or harmful.
In particular, a normal argmax with a combined spam+scam score meeting the review
threshold belongs under Review, not No high risk detected. Unrecognised states
or labels belong under Review rather than receiving an invented normal result.
Missing or invalid decision metadata must not be promoted into the reassuring
normal category. Confirm that such legacy records display a review explanation
and a review color rather than a green result.
Only an incoming **scam** decision can trigger the existing automatic warning;
including spam in the Harmful browsing category does not change alert policy.

## Updating results while browsing

While a synthetic inbox scan is running, move between filters and pages. Check
that completed and pending results enter the right categories, stale background
responses do not repaint a newly selected filter, and a shrinking category
does not leave an invalid empty page. Refresh should show current stored results.
Browsing, filtering, paginating and refreshing must not delete private records,
reclassify completed messages, modify system SMS, or reveal clickable links.

## Execution evidence

The prepared `AppFlowInstrumentation` performs synthetic private-database and UI
checks against the debug application only. It deliberately preserves its test
records and does not send real SMS, grant SMS permissions or clear existing data.
Report it as compiled but not executed unless a matching device run is saved.
The full carrier-SMS, alert privacy and Samsung background-behavior checklist
in [DASHBOARD_DEVICE_QA.md](DASHBOARD_DEVICE_QA.md) still applies.
