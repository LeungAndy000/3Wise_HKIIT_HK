# Domain v2 source-documentation clarification

The `mudou_sms.semantics` paragraph in the immutable `manifest.json` and
`source_documentation.json` was inherited from the baseline. Its statement that
all source spam rows are excluded from training describes the baseline only.
The domain v2 `partial_supervision` and `revision_preparation` manifest fields
describe the actual revision correctly.

Domain v2 keeps baseline normal-labelled Mudou training messages as normal=0.
It adds 2,801 original unwanted messages from the source TRAIN file, yielding
5,562 training rows after Traditional Chinese augmentation. These have
`label=-1`, `risk_label=1`, and `supervision=binary_unwanted`; their loss is
`-log(P(spam)+P(scam))`. Their unknown fine-grained subtype is not relabelled as
either advertising spam or scam. Separate groups supply 350 validation and 350
reserved-test unwanted messages. The binary-domain test also includes 296
explicitly identified normal messages from the baseline held-out test.

The source's original TEST file remains a previously observed development
diagnostic. Its original 959 prepared rows are preserved; four documented
text-similarity exclusions leave 955 evaluated rows. It does not establish
independent spam-versus-scam subtype accuracy.

The training manifest, source-documentation file, JSONL data, and recorded file
hashes have not been changed by this clarification. Future revisions generated
with `wisemessage.data_domain` contain the corrected source semantics.

Read-only verification:

```bash
python -B -m wisemessage.data_domain --audit-only --output-dir data/prepared_domain_v2
```

This rechecks dataset-file SHA256 values and inspects the stored separation
audit. It does not recompute grouping or write files. To reproduce preparation,
select a new, empty output directory:

```bash
python -B -m wisemessage.data_domain --baseline-dir data/prepared --output-dir data/prepared_domain_v3
```
