# WiseMessage Android development package

The WiseMessage Android application detects normal, spam and scam SMS on the phone with MindSpore Lite. This directory contains application source, model code, trained weights, datasets and validation reports.

## What is included

| Directory | Role |
| --- | --- |
| `android/` | Android application source, bundled detection model and native runtime |
| `windows-app/` | Launcher for the Android application in the existing local WSLg emulator |
| `wisemessage/` | Native MindSpore encoder, classifier, tokenization, training, prediction and evaluation |
| `scripts/`, `tests/` | Application launchers, model utilities, conversion, validation and unit tests |
| `data/raw/` | Downloaded original dataset archives and source documentation |
| `data/prepared/` | Immutable baseline dataset revision |
| `data/prepared_domain_v2/` | Current training, validation and evaluation revision |
| `artifacts/pretrained/` | Converted pretrained encoder; no trained SMS classification head |
| `artifacts/sources/minirbt/` | Source checkpoint, extracted tensors and source attribution |
| `artifacts/runs/initial_retry1/model/` | Earlier model checkpoint |
| `artifacts/runs/domain_v2_20261023_1050/` | Current trained SMS detector and its recorded results |
| `artifacts/conversion_validation/`, `artifacts/data_audit/` | Saved conversion-parity and dataset-exclusion evidence |
| `docs/` | Selected technical documentation and validation context |

Installable packages are in the [release folder](../release/README.md). Recorded application checks are in [validation evidence](<../Validation Evidence/README.md>).

## Run the Android application

To run the Android application on Windows, double-click [windows-app/Launch-WiseMessage.cmd](windows-app/Launch-WiseMessage.cmd). It launches the APK in an Android emulator through WSLg. Follow [the emulator guide](windows-app/README.md) for SDK, AVD and permission requirements.

The Android SDK, emulator system image, provisioned AVD, Java and WSL distribution must be installed separately. Configure their paths in `windows-app/emulator-settings.json` for the target computer.

For a physical Android phone, follow the [installation guide](android/README.md#install-for-a-controlled-phone-test). Building the APK is covered in [android/BUILDING.md](android/BUILDING.md). From PowerShell in this `Project` directory, an offline build using provisioned toolchains and caches is:

```powershell
.\scripts\build_android.ps1 -Offline -ReuseNative
```

Installing the supplied signed APK does not require signing files. Rebuilding requires the existing private signing identity through `WISEMESSAGE_SIGNING_DIR`; see [BUILDING.md](android/BUILDING.md). Signing keys and password properties are kept outside this submission folder.

The application interface supports Traditional Chinese, Simplified Chinese and English. English interface support does not establish English-message detection accuracy. SMS access and notifications depend on Android permissions and device settings. Emulator verification and physical-phone verification are separate forms of evidence.

## Native model and dataset roles

Use `artifacts/runs/domain_v2_20261023_1050/model` for current native SMS detection. Keep its checkpoint, configuration, vocabulary, classifier manifest and performance report together. The predictor verifies identities and loads model parameters strictly. Android uses the converted model bundled under `android/app/src/main/assets/wisemessage`, with its own recorded parity and packaging checks.

The native detector has six Transformer encoder layers, hidden size 256, eight attention heads and a three-category classifier. It contains 10,280,195 parameters. Training fine-tuned the encoder and classifier together; the pretrained encoder alone cannot classify SMS. PyTorch is not used for current native training or detection.

The current model was trained with `data/prepared_domain_v2`. This revision contains 65,336 training rows and 4,339 validation rows. Validation selected the checkpoint and review threshold; test roles and data ancestry are recorded in the dataset manifests and [validation report](docs/VALIDATION_RESULTS.md).

| Recorded evaluation | Messages | Reported score |
| --- | ---: | ---: |
| Original grouped normal/spam/scam test, previously inspected | 2,488 | 98.61% macro F1 |
| Paired Traditional Chinese conversion | 2,488 | 98.83% macro F1 |
| Reserved raw unwanted SMS plus reused normal examples | 646 | 94.25% binary F1 |
| Case-grouped generated normal/scam examples | 1,500 | 99.40% present-class macro F1 |

The Traditional Chinese conversion is paired data, and generated examples are not captured real SMS. The raw binary test measures normal versus unwanted messages. These distinct evaluation roles must remain visible when reporting quality. See [dataset repair documentation](docs/DATASET_BIAS_AND_REPAIR.md) and `data/prepared_domain_v2/ERRATA.md` for the development history and source-label clarification.

The current model ID is `wisemessage-minirbt-h256-step1221`. Its checkpoint SHA-256 is `940913e59a1142aa36679d1b885b71183e0464b075c792c26204c27bd75775ae`.

## Python inference prerequisites

Python inference requires a compatible Linux environment with Python 3.12 and MindSpore 2.10.0. Windows users can use WSL Ubuntu. `requirements.txt` records runtime dependencies; `requirements-dev.txt` adds pytest and HTTP API test dependencies. Activate the appropriate Python environment before running the commands below.

GPU inference also requires an NVIDIA driver, WSL GPU support when applicable, and compatible CUDA libraries. Configure these Linux environment variables to match the installed libraries:

| Variable | Meaning |
| --- | --- |
| `WISEMESSAGE_CUDA_HOME` | CUDA toolkit directory; takes precedence over `CUDA_HOME` |
| `WISEMESSAGE_NVIDIA_LIBRARY_ROOT` | Optional Python `site-packages/nvidia` directory containing library subdirectories |
| `WISEMESSAGE_CUDA_LIBRARY_DIRS` | Optional colon-separated additional native library directories |

Set library overrides in the environment used to launch Python. Existing `PATH` and `LD_LIBRARY_PATH` entries are preserved. PowerShell variables are not automatically exported into WSL.

## Tests and inference

Run these commands from this `Project` directory in the activated Python environment to check dataset hashes and run tests:

```bash
python -B -m wisemessage.data --audit-only --output-dir data/prepared
python -B -m wisemessage.data_domain --audit-only --output-dir data/prepared_domain_v2
python -B -m pytest -q -p no:cacheprovider tests
```

For CPU inference:

```bash
python -B -m wisemessage predict \
  --model-dir artifacts/runs/domain_v2_20261023_1050/model \
  --device-target CPU --message '明天上午十點開會。'
```

For GPU inference, establish library paths before a fresh Python process imports MindSpore:

```bash
python -B scripts/run_wisemessage_gpu.py -- predict \
  --model-dir artifacts/runs/domain_v2_20261023_1050/model \
  --device-target GPU --message '明天上午十點開會。'
```

Each response includes category scores, model identity, the predicted category and a review decision. A score is a model estimate, not authentication of the sender. Native inference reads at most 256 WordPiece tokens.

To check the current model through CPU prediction, CLI and a loopback API:

```bash
python -B scripts/validate_runtime.py
```

This operation writes reports under the selected model run's `runtime_validation` directory. It verifies operation rather than estimating accuracy. `wisemessage.service` provides an optional API and is used by the tests. API operation binds to `127.0.0.1` by default:

```bash
python -B -m wisemessage serve \
  --model-dir artifacts/runs/domain_v2_20261023_1050/model \
  --device-target CPU --host 127.0.0.1 --port 8011
```

## Conversion and recorded evidence

`artifacts/sources/minirbt` contains the source checkpoint pinned to revision `446e1b4012b10946f479563005700c54c9db3f7c`, its extracted tensor archive and provenance. `artifacts/pretrained` contains the native encoder conversion. The recorded parity report is `artifacts/conversion_validation/parity.json`; the final measured results are `artifacts/runs/domain_v2_20261023_1050/evaluation/performance.json`.

Inference and tests use the included model files. Optional source-reference regeneration with `scripts/validate_minirbt_conversion.py reference` requires a separate CPU PyTorch/Transformers environment; those packages are not part of the native runtime requirements. Use new output directories when regenerating conversion or evaluation artifacts to preserve existing results.

Source code and the pretrained encoder have Apache 2.0 notices. Dataset permissions differ; source terms are recorded in `data/prepared/source_documentation.json` and the current revision's source documentation. Preserve `LICENSE.txt`, `NOTICE.txt` and source provenance when transferring this private research package.
