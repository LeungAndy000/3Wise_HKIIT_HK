# WiseMessage on-device Android model

The Android application embeds the existing supervised WiseMessage checkpoint.
It performs native MindSpore Lite CPU inference entirely on the phone. It does
not call a server, retrain the network, or replace its outputs with text rules.

The source checkpoint is `artifacts/runs/domain_v2_20261023_1050/model/model.ckpt`,
SHA-256 `940913e59a1142aa36679d1b885b71183e0464b075c792c26204c27bd75775ae`.
The bundled `model.ms` is 40,934,864 bytes, SHA-256
`5f5af31d7aec95abe514203e547b7fdcf0df83e70f6c3924481907c487b332de`.

## Conversion and validation

Run these commands from the WiseMessage project directory in a compatible WSL
MindSpore environment with the required conversion tools installed.

```bash
python android/model-tools/download_lite.py
python scripts/export_android_model.py --portable-scalars \
  --output-dir artifacts/android/export_v2
python android/model-tools/convert_lite.py --export-dir artifacts/android/export_v2
python android/model-tools/validate_lite.py --export-dir artifacts/android/export_v2
python android/model-tools/validate_lite_corpus.py
python android/model-tools/package_assets.py
```

If a streaming Android archive download stalls, `download_android_ranges.py`
downloads checked HTTP byte ranges and verifies the same official archive hash.
`inspect_android_runtime.py` records the upstream shared libraries' ELF layout.

MindSpore 2.10 emits a scalar division operation called `Divs` that the official
2.7.1 end-side converter does not support correctly. The direct export in
`export_v1` therefore failed parity despite the converter returning success.
`portable_network.py` materializes the two compile-time scalar reciprocals as
FP32 tensors and multiplies by them. It retains all original trained parameters,
exact erf GELU, attention mask, layer normalization and classifier behavior.
The export script checks this wrapper against the original network before
packaging. Maximum original/wrapper logit difference on 96 samples is 1.23e-5.

The converted end-side model agrees with the original network on all 96 parity
sample classes, with maximum probability difference 7.81e-6. Revalidation on
all 9,577 previously reported labelled evaluation messages preserves every
class decision and every binary unwanted-message decision. Maximum difference
from saved native MindSpore GPU probabilities across these six tests is 6.32e-6.
The machine-readable results are in:

- `artifacts/android/export_v2/lite_parity.json`
- `artifacts/android/full_corpus_v1/report.json`
- `artifacts/android/export_v2/packaging.json`

These are host x86 CPU checks. Actual Samsung latency, battery use and ARM64
execution need to be checked on the phone. The underlying dataset limitations
in the project's validation report still apply.

## Android native runtime and 16 KB pages

The official MindSpore Lite 2.7.1 Android archive is downloaded from the URL in
`artifacts/android/tools/android_download.json` and pinned to SHA-256
`c67605f4ab2dab083c7c6c8bf7167c95e650de8845090e5572a081e14547e72e`.
Its prebuilt shared libraries have 4 KB ELF load-segment alignment. The app
therefore does not package those shared libraries or their AAR files.

`build_android_native.py` uses NDK r28 or later to link the unchanged official
ARM64 static library and securec archive, the complete kernel registry, and a
small JNI bridge into a new `libwisemessage_native.so`. The actual linker uses
16 KB maximum/common page sizes and static libc++; no ELF headers are patched.
The script validates every load segment's alignment and offset/address
congruence and records the complete command and `llvm-readelf` output.

```bash
python android/model-tools/build_android_native.py --ndk /path/to/android-ndk-r28c
```

The bridge class is `hk.wisemessage.app.ml.NativeMessageEngine`. Its three
methods are `create(ByteBuffer, int)`, `predict(long, int[], int[], int[])`,
and `destroy(long)`. It requires three int32 inputs named `input_ids`,
`attention_mask`, `token_type_ids`, each `[1, 256]`, and returns three FP32
logits in normal/spam/scam order. Java applies stable softmax. A scam alert uses
the validated three-class argmax decision; unwanted-message review uses
`P(spam) + P(scam) >= 0.5`.

Assets reside in `android/app/src/main/assets/wisemessage`. Their manifest
includes model/vocabulary hashes and the deployment interface. The
`parity_cases.json` asset contains 24 diverse tokenizer fixtures and 96 original
checkpoint fixtures with token IDs and reference probabilities.
