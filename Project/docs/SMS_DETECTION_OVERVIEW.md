# WiseMessage SMS detection overview

WiseMessage uses one local classifier for three text-input routes:

1. New carrier SMS delivered through the required phone permissions.
2. Existing inbox SMS, after separate consent and `READ_SMS` access.
3. Text entered for a manual check.

Each route passes through a local queue, tokenization, MindSpore Lite inference and result storage. Incoming messages may then qualify for a warning. The current APK does not extract text from screenshots or images and does not scan RCS/chat, WhatsApp, email or other applications.

## Model and decisions

WordPiece tokenization feeds a compact BERT-family encoder with six layers and 256 hidden features. A trained three-output classifier produces normal, spam and scam scores. The highest score determines the predicted category. These scores do not verify the sender's identity.

The model accepts 256 token positions, including `[CLS]` and `[SEP]`. Longer text is truncated and flagged; evidence near the end of a long message may be missed.

Result review and automatic warnings are different decisions:

- **Harmful:** completed spam/scam decisions or an explicit stored scam flag.
- **No high risk detected:** a completed normal result with the required flags explicitly clear. This is not proof of legitimacy.
- **Review or unfinished:** uncertain, waiting, failed or incomplete checks.
- **All results:** every private result, including unfinished checks.

Automatic warning eligibility requires a newly completed **incoming** check classified as scam, with monitoring, required SMS access and warning notifications enabled. Inbox and manual checks do not create the same incoming-SMS alert. A normal-argmax result can be marked for review when `P(spam) + P(scam) >= 0.5`; automatic scam warnings use the scam argmax decision rather than an additional 0.5 scam-score condition.

## User controls and local storage

The dashboard shows permission/protection status and daily counts. Green describes enabled protection, not guaranteed prevention. Inbox and result browsing use separate pages and filters. Received and checked counts use their respective receipt and successful-completion dates.

The current app requests neither Internet nor SMS-sending permission. Inference and private records stay on the phone. The app does not replace the default messaging app or bypass Android delivery and background restrictions. Permissions, notification channels, battery settings and operating-system limits can affect receipt and warning visibility.

Traditional Chinese, Simplified Chinese and English are interface options. English-message detection accuracy still needs separate evaluation. Verify suspicious requests through official contact details obtained independently before acting.

See [Android implementation and permissions](../android/README.md), [model validation](VALIDATION_RESULTS.md), [dataset preparation](DATASET_BIAS_AND_REPAIR.md) and the recorded [Android upgrade validation](../artifacts/android/v3_2_upgrade_validation.json).
