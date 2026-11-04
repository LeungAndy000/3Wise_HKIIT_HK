"""Package only a parity-verified Lite model and exact tokenizer fixtures."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

EXTRA_CASES = [
    "明天下午三點覆診，請帶同身份證。", "明天下午三点复诊，请带上身份证。",
    "媽，我今晚七點返屋企食飯，唔使等我買餸。", "您的帳戶異常，請立即提供驗證碼以免凍結。",
    "您的账户异常，请立即提供验证码以免冻结。", "職員不會索取密碼或驗證碼，切勿轉發給任何人。",
    "验证码 728416，五分钟内有效，请勿告诉任何人。", "Visit HTTPS://Example.INVALID/pay?id=ABC123&x=1 now!",
    "Win $1000! Call +852 9123 4567. Reply STOP.", "Hello\tWORLD\nCafé naïve résumé",
    "\u0000\u0001帳戶\u0007\u0008異常\u007f", "\u200b請\ufeff核實\u200d身份",
    "全城傢俬清貨！低至三折，歡迎到店查詢。", "您好，您的包裹已送达，请在原购物平台查看。",
    "【银行通知】转账到所谓“安全账户”！", "🎉恭喜中獎💰請付手續費📦",
    "ＳＭＳ　１２３４５　ＡＢＣａｂｃ", "中文English123混合，網址：a.invalid/登入。",
    "𠀀𠮷漢字测试", "A" * 101, "x " * 400, "驗證碼" * 200,
    "can't won't mail@example.invalid path/to-file_v2", "One\r\nTwo\u00a0Three\u3000四",
]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    import numpy as np
    from wisemessage.tokenizer import MessageTokenizer
    source = ROOT / "artifacts/runs/domain_v2_20261023_1050/model"
    export = ROOT / "artifacts/android/export_v2"
    assets = ROOT / "android/app/src/main/assets/wisemessage"
    parity = json.loads((export / "lite_parity.json").read_text())
    if not parity["passed"] or parity["argmax_agreement"] != 1:
        raise RuntimeError("Cannot package a model that failed native/Lite parity")
    manifest = json.loads((source / "manifest.json").read_text())
    if parity["source_checkpoint_sha256"] != manifest["checkpoint_sha256"]:
        raise RuntimeError("Wrong trained checkpoint")
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(export / "wisemessage.ms", assets / "model.ms")
    shutil.copy2(source / "vocab.txt", assets / "vocab.txt")
    tokenizer = MessageTokenizer(source / "vocab.txt", 256, True)
    extra = tokenizer.encode_batch(EXTRA_CASES)
    cases = []
    for index, text in enumerate(EXTRA_CASES):
        cases.append({"id": f"tokenizer-{index:02d}", "text": text,
                      **{key: value[index].tolist() for key, value in extra.items()}})
    encoded = np.load(export / "parity_inputs.npz")
    logits = np.load(export / "reference_logits.npy")
    probabilities = np.exp(logits - logits.max(1, keepdims=True))
    probabilities /= probabilities.sum(1, keepdims=True)
    texts = json.loads((export / "parity_texts.json").read_text())
    for index, text in enumerate(texts):
        cases.append({"id": f"checkpoint-{index:03d}", "text": text,
                      **{key: encoded[key][index].tolist() for key in encoded.files},
                      "probabilities": probabilities[index].tolist()})
    (assets / "parity_cases.json").write_text(json.dumps(cases, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    mobile_manifest = {
        "format_version": 1,
        "model_id": manifest["model_id"], "model_file": "model.ms",
        "model_sha256": digest(assets / "model.ms"), "vocab_file": "vocab.txt", "vocab_sha256": digest(assets / "vocab.txt"),
        "source_checkpoint_sha256": manifest["checkpoint_sha256"], "source_framework": "mindspore", "source_framework_version": "2.10.0",
        "runtime": "MindSpore Lite", "runtime_version": "2.7.1", "model_format": "MINDIR_LITE", "device": "CPU", "enable_fp16": False,
        "max_length": 256, "vocab_size": 21128, "do_lower_case": True,
        "input_names": ["input_ids", "attention_mask", "token_type_ids"], "input_shape": [1, 256], "input_dtype": "int32",
        "output_shape": [1, 3], "output_dtype": "float32", "output_semantics": "logits_softmax_required",
        "labels": ["normal", "spam", "scam"], "unwanted_threshold": 0.5,
        "scam_decision": "argmax_scam", "scam_threshold": 0.5,
        "scam_threshold_note": "Reserved UI setting; validated three-class decision uses argmax_scam, without an extra probability cutoff.",
        "conversion_validation": parity,
        "limitations": ["Host x86 CPU parity does not establish Samsung device latency or ARM64 runtime behavior.",
                        "Classifier scores are estimates, not verified sender identity.", "Messages longer than 254 WordPiece tokens are truncated."],
        "license": "Research prototype; see NOTICE.txt and dataset source terms.",
    }
    (assets / "manifest.json").write_text(json.dumps(mobile_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(ROOT / "NOTICE.txt", assets / "NOTICE.txt")
    shutil.copy2(ROOT / "LICENSE.txt", assets / "LICENSE.txt")
    report = {"assets": {path.name: {"sha256": digest(path), "bytes": path.stat().st_size} for path in assets.iterdir() if path.is_file()},
              "tokenizer_fixture_samples": len(EXTRA_CASES), "model_parity_samples": len(texts), "passed": True}
    (export / "packaging.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)

if __name__ == "__main__":
    main()
