# WiseMessage validation results

The recorded evaluation was completed on 23 October 2026 using native
**MindSpore 2.10**. The final model is
`wisemessage-minirbt-h256-step1221`.

The portable bundle is in
`artifacts/runs/domain_v2_20261023_1050/model`. It contains the complete trained
six-layer MiniRBT-H256 encoder, three-class classifier, configuration, Chinese
vocabulary, strict identity manifest, and performance report.

- Trainable parameters: **10,280,195**, including the **771-parameter** classifier.
- Checkpoint: **41,126,975 bytes** (41.1 MB).
- Final checkpoint SHA256:
  `940913e59a1142aa36679d1b885b71183e0464b075c792c26204c27bd75775ae`.
- Model revision: **3 epochs and 1,221 updates**, initialized from the earlier
  six-epoch classifier.
- All six encoder layers and the classifier were trainable. Unknown unwanted
  subtypes used partial-label loss instead of fabricated spam/scam labels.
- Validation selected epoch 3 and aggregate review threshold
  `P(spam)+P(scam) >= 0.5`. Tests did not select checkpoints or thresholds.

## Measured performance

| Evaluation | Messages | F1 | Relevant recall | Normal false-positive rate |
| --- | ---: | ---: | ---: | ---: |
| Original grouped normal/spam/scam test | 2,488 | **98.61% macro** | 99.69% scam | 2.48% |
| Paired Traditional Chinese conversion of that test | 2,488 | **98.83% macro** | 99.69% scam | 2.10% |
| Newly reserved raw SMS domain test, normal/unwanted | 646 | **94.25% binary** | 93.71% unwanted | 6.08% |
| Newly reserved case-grouped generated SMS, normal/scam | 1,500 | **99.40% present-class macro** | 99.60% scam | 0.80% |
| Paired Traditional Chinese conversion of generated SMS | 1,500 | **99.25% present-class macro** | 99.50% scam | 0.99% |
| Previously seen external normal/unwanted diagnostic | 955 | **96.85% binary** | 95.68% unwanted | 6.51% |

Binary scores use the application's aggregate review decision. The generated
normal/scam sets contain no gold spam class, so their macro F1 averages the
two present classes. Misclassification as spam still counts against their
normal/scam precision and recall. These scores are not interchangeable with
three-class or independent real-world scam accuracy.

The new binary-domain set contains **350 newly reserved unwanted SMS** and
**296 explicitly paired normal examples** from the original test. The original
main, converted, and external files were already evaluated before the repair
and remain development diagnostics. The new FGRC case groups and raw unwanted
groups were reserved before repair training. All revision training/validation/
test pairs have zero canonical-text, normalized-template, 256-token-input,
group, and available FGRC case-ID overlap. The older Telecom corpus lacks
case IDs, so cross-source case independence cannot be fully guaranteed.

The initial model's external unwanted F1 was only **0.27%**. Its high internal
F1 concealed source-format bias. The dataset revision addressed this issue
through domain-aware supervision. See [dataset revision](DATASET_BIAS_AND_REPAIR.md).

## Runtime verification

- Official Hugging Face versus converted MindSpore encoder: exact token IDs;
  maximum hidden-state difference **1.62e-5** on eight mixed-script examples.
- **31 unit and contract tests passed**, including loss/gradient stability,
  partial-label quality gates, manifest integrity, API validation, and GPU CLI
  environment bootstrap.
- The final checkpoint loaded strictly on CPU and GPU. Actual FastAPI health,
  prediction, and single-message endpoints succeeded; invalid input returned
  HTTP 422.
- Actual CPU, API, and CLI probabilities matched exactly; all returned the
  selected aggregate threshold and decisions consistently.
- Four saved CPU/GPU demonstration outputs matched within **2.89e-8** maximum
  class-probability difference. This is runtime parity, not an accuracy test.
- GPU length-bucket versus fixed-padding probability difference was at most
  **1.79e-7** on 64 test examples; public predictor versus evaluator was exact.

Detailed machine-readable reports:

- `artifacts/runs/domain_v2_20261023_1050/evaluation/performance.json`
- `artifacts/runs/domain_v2_20261023_1050/runtime_validation/report.json`
- `artifacts/runs/domain_v2_20261023_1050/runtime_validation/device_parity.json`
- `data/prepared_domain_v2/data_audit.json`
- `artifacts/domain_v2_unit_tests_after_calibration.xml`

## Scope of qualification

All provisional validation and measured-dataset checks passed. This remains a
**research prototype**, with `production_ready=false` in its result. FGRC texts
are generated from cases; their normal examples often contain anti-fraud
guidance, so generated-source bias remains possible. Dataset licenses and
upstream permissions also differ.

Traditional Chinese is supported in training and runtime and passed the paired
conversion tests. The original test contains only three native Traditional
Chinese examples. A substantial independently labelled Hong Kong/Taiwan SMS
benchmark, including Cantonese and current scams, is still required before a
public pilot. Class scores and review flags do not authenticate a sender.
