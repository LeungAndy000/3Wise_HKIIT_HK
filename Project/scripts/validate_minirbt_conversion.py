"""Cross-framework parity against official Hugging Face BertModel on Chinese text."""

import argparse
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

TEXTS = [
    "您好，您的快递已到驿站，请凭取件码领取。",
    "您好，您的快遞已到服務站，請憑取件碼領取。",
    "您的銀行帳戶需要驗證，請立即登入 https://example.com。",
    "妈妈，我换了电话号码，急需你转钱。",
    "阿媽，我換咗電話，急需你轉錢。",
    "【Bank】Your OTP 驗證碼 123456，切勿向任何人透露。",
    "超值促销！全场五折，立即选购。",
    "今晚七點見。",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("reference", "native"))
    parser.add_argument("--source-dir", default="artifacts/sources/minirbt")
    parser.add_argument("--model-dir", default="artifacts/pretrained")
    parser.add_argument("--output-dir", default="artifacts/conversion_validation")
    args = parser.parse_args()
    source, model_dir, output = Path(args.source_dir), Path(args.model_dir), Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if args.phase == "reference":
        sys.path.insert(0, str(PROJECT / "artifacts/tools/hf_reference"))
        import numpy as np
        import torch
        import transformers
        from transformers import BertConfig, BertModel, BertTokenizerFast
        config = BertConfig.from_json_file(source / "config.json")
        config._attn_implementation = "eager"
        reference = BertModel(config, add_pooling_layer=False).eval()
        state = torch.load(source / "pytorch_model.bin", map_location="cpu", weights_only=True)
        expected = reference.state_dict()
        filtered = {name: state["bert." + name] for name in expected}
        reference.load_state_dict(filtered, strict=True)
        tokenizer = BertTokenizerFast(vocab_file=str(source / "vocab.txt"), do_lower_case=True)
        encoded = tokenizer(TEXTS, padding="max_length", truncation=True, max_length=96, return_tensors="pt")
        with torch.no_grad():
            hidden = reference(**encoded).last_hidden_state.numpy()
        values = {key: value.numpy().astype(np.int32) for key, value in encoded.items()}
        values["last_hidden_state"] = hidden
        np.savez(output / "reference.npz", **values)
        info = {"texts": TEXTS, "torch_version": torch.__version__, "transformers_version": transformers.__version__,
                "reference": "transformers.BertModel official eager implementation", "max_length": 96,
                "samples": len(TEXTS), "hidden_shape": list(hidden.shape), "safe_weights_only": True}
        (output / "reference.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(info, ensure_ascii=False))
    else:
        import numpy as np
        from wisemessage.runtime import configure_runtime
        ms = configure_runtime("CPU")
        from wisemessage.config import MessageConfig
        from wisemessage.model import MessageClassifier
        from wisemessage.tokenizer import MessageTokenizer
        config = MessageConfig.from_json(model_dir / "config.json")
        network = MessageClassifier(config)
        missing, unexpected = ms.load_param_into_net(network, ms.load_checkpoint(str(model_dir / "model.ckpt")), strict_load=True)
        if set(missing) != {"classifier.weight", "classifier.bias"} or unexpected:
            raise ValueError(f"Encoder load mismatch: missing={missing}, unexpected={unexpected}")
        network.set_train(False)
        reference = np.load(output / "reference.npz", allow_pickle=False)
        tokenizer = MessageTokenizer(model_dir / "vocab.txt", max_length=96)
        encoded = tokenizer.encode_batch(TEXTS)
        tokenizer_match = all(np.array_equal(encoded[key], reference[key]) for key in encoded)
        if not tokenizer_match:
            raise AssertionError("Native tokenizer differs from official HF tokenizer")
        actual = network.bert(*(ms.Tensor(encoded[key], ms.int32) for key in ("input_ids", "attention_mask", "token_type_ids"))).asnumpy()
        expected = reference["last_hidden_state"]
        maximum = float(np.max(np.abs(actual - expected)))
        mean = float(np.mean(np.abs(actual - expected)))
        passed = bool(np.allclose(actual, expected, rtol=2e-4, atol=5e-5))
        result = {"passed": passed, "framework": "mindspore", "mindspore_version": ms.__version__,
                  "reference": "official Hugging Face BertModel 4.44.2", "device_target": "CPU",
                  "samples": len(TEXTS), "scripts": ["Simplified Chinese", "Traditional Chinese", "Cantonese", "mixed English"],
                  "tokenizer_exact_match": tokenizer_match, "max_abs_error": maximum, "mean_abs_error": mean,
                  "rtol": 2e-4, "atol": 5e-5, "compared": "all last-layer sequence hidden states",
                  "classifier_untrained_not_compared": True}
        (output / "parity.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        if not passed:
            raise AssertionError("MindSpore encoder parity failed")


if __name__ == "__main__":
    main()
