# SMS domain failure and repair

The initial WiseMessage classifier used a MiniRBT-H256 encoder with a three-class
SMS classification head. Its internal scores did **not** establish useful SMS
generalization.

| Initial evaluation | Result |
| --- | --- |
| Grouped three-class test, 2,488 messages | Macro F1 99.66%; scam recall 99.84% |
| Paired Traditional Chinese conversion, 2,488 messages | Macro F1 99.66% |
| Separate binary SMS test, 955 messages | Unwanted F1 0.27%; recall 0.14% |

The binary external test has 740 unwanted and 215 normal messages after four
text-identity exclusions. The initial model missed 739 unwanted messages. This
result showed that the internal evaluation did not represent the separate SMS
source. Handwritten credential request examples were also incorrectly predicted
normal; these examples are
diagnostics, not an accuracy benchmark and are not added as training targets.

## Cause

In the initial dataset, Mudou supplied only normal-labelled training rows. Its
unwanted rows were omitted because the source does not distinguish advertising
spam from fraud. The three-way model consequently saw raw SMS style associated
with normal, while advertising spam came entirely from preprocessed FBS SMS.
96.9% of the FBS-derived spam training texts contain source anonymization markers.
Most other fraud supervision came from longer, case-derived dialogue. A model
can learn those source cues even when exact and near-duplicate text groups are
properly separated. Correct code, conversion parity, and internal held-out
scores do not eliminate this form of domain bias.

## Revised supervision

The separate `data/prepared_domain_v2` revision retains the original files and
adds short message-form supervision:

- Original Mudou training-file unwanted messages receive `label=-1`,
  `risk_label=1`, and `supervision=binary_unwanted`. Their unknown spam/scam
  subtype is preserved.
- Fully labelled normal, spam, and scam messages retain their three-class labels.
- FGRC-SCD contributes additional message-form normal and fraud examples,
  grouped by case ID before splitting. They are generated from cases, rather
  than independently captured real SMS. Their provenance remains explicit.
- Traditional Chinese training variants are created only after splitting.
  Text, normalized templates, and token identities are checked across splits.

For complete labels, the loss is weighted three-class cross entropy. For an
unwanted message with unknown subtype, the loss is
`-log(P(spam) + P(scam))`. This teaches the model to recognize risk without
fabricating a fraud label. All six encoder layers and the classifier are
fine-tuned. The initial trained checkpoint is a warm start; no held-out test
message becomes a training example.

The application exposes all three class scores and a combined unwanted score.
For the revised model, the review threshold on `P(spam)+P(scam)` is selected
using validation only. A review flag can therefore remain useful when the
spam/scam subtype is uncertain.

## Validation protocol and limits

The original external file informed the model revision and is therefore a
**seen diagnostic**, not a fresh independent confirmation. New grouped
Mudou-domain and case-grouped FGRC test
rows are reserved before revised training. Checkpoints and thresholds use
validation only. Reports keep three-class, binary, case-derived, and paired
script-conversion results separate.

Provisional measured-dataset requirements are macro F1 and scam recall at least
0.80, normal false-positive rate at most 0.10, and binary unwanted F1 and recall
at least 0.80 on the applicable binary sets. The FGRC normal/scam subset uses
macro F1 over its present classes. Passing these checks still does not establish
production readiness or native Hong Kong/Taiwan SMS performance. Converted
Traditional Chinese examples are not a substitute for an independently labelled
native-script benchmark. Dataset permissions also limit this combination to a
research prototype; see the source documentation and notices.
