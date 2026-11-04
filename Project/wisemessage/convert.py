"""Audited, exact-shape HF MiniRBT encoder to native MindSpore conversion.

PyTorch is isolated to the source extraction step with weights_only=True.
The native runtime uses only a pickle-free NPZ bridge and MindSpore.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
from .config import MessageConfig


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def encoder_weight_map(config):
    hidden, intermediate = config.hidden_size, config.intermediate_size
    result = {
        "bert.embeddings.word_embeddings.weight": ("bert.embeddings.word_embeddings.embedding_table", (config.vocab_size, hidden)),
        "bert.embeddings.position_embeddings.weight": ("bert.embeddings.position_embeddings.embedding_table", (config.max_position_embeddings, hidden)),
        "bert.embeddings.token_type_embeddings.weight": ("bert.embeddings.token_type_embeddings.embedding_table", (config.type_vocab_size, hidden)),
        "bert.embeddings.LayerNorm.weight": ("bert.embeddings.layer_norm.gamma", (hidden,)),
        "bert.embeddings.LayerNorm.bias": ("bert.embeddings.layer_norm.beta", (hidden,)),
    }
    for index in range(config.num_hidden_layers):
        source, target = f"bert.encoder.layer.{index}.", f"bert.layers.{index}."
        for projection in ("query", "key", "value"):
            for suffix, shape in (("weight", (hidden, hidden)), ("bias", (hidden,))):
                result[f"{source}attention.self.{projection}.{suffix}"] = (f"{target}attention.{projection}.{suffix}", shape)
        for original, native, shape in (
            ("attention.output.dense.weight", "attention_output.weight", (hidden, hidden)),
            ("attention.output.dense.bias", "attention_output.bias", (hidden,)),
            ("attention.output.LayerNorm.weight", "attention_layer_norm.gamma", (hidden,)),
            ("attention.output.LayerNorm.bias", "attention_layer_norm.beta", (hidden,)),
            ("intermediate.dense.weight", "intermediate.weight", (intermediate, hidden)),
            ("intermediate.dense.bias", "intermediate.bias", (intermediate,)),
            ("output.dense.weight", "output_dense.weight", (hidden, intermediate)),
            ("output.dense.bias", "output_dense.bias", (hidden,)),
            ("output.LayerNorm.weight", "output_layer_norm.gamma", (hidden,)),
            ("output.LayerNorm.bias", "output_layer_norm.beta", (hidden,)),
        ):
            result[source + original] = (target + native, shape)
    return result


def discarded_shapes(config):
    h, v = config.hidden_size, config.vocab_size
    return {
        "cls.predictions.bias": (v,), "cls.predictions.decoder.weight": (v, h),
        "cls.predictions.decoder.bias": (v,),
        "cls.predictions.transform.dense.weight": (h, h),
        "cls.predictions.transform.dense.bias": (h,),
        "cls.predictions.transform.LayerNorm.weight": (h,),
        "cls.predictions.transform.LayerNorm.bias": (h,),
        "bert.pooler.dense.weight": (h, h), "bert.pooler.dense.bias": (h,),
        "bert.embeddings.position_ids": (1, config.max_position_embeddings),
        "bert.embeddings.token_type_ids": (1, config.max_position_embeddings),
    }


def map_numpy_state(state, config):
    mapping, allowed = encoder_weight_map(config), discarded_shapes(config)
    missing = set(mapping) - set(state)
    unknown = set(state) - set(mapping) - set(allowed)
    if missing or unknown:
        raise ValueError(f"Checkpoint mismatch: missing={sorted(missing)}, unexpected={sorted(unknown)}")
    native = {}
    for name, values in state.items():
        expected = mapping[name][1] if name in mapping else allowed[name]
        if values.shape != expected:
            raise ValueError(f"{name}: shape {values.shape}, expected {expected}")
        if name.endswith("position_ids"):
            if not np.array_equal(values, np.arange(config.max_position_embeddings)[None, :]):
                raise ValueError("Position buffer mismatch")
        elif name.endswith("token_type_ids"):
            if np.any(values != 0):
                raise ValueError("Token type buffer mismatch")
        elif values.dtype != np.float32 or not np.isfinite(values).all():
            raise ValueError(f"{name}: weights must be finite float32")
        if name in mapping:
            native[mapping[name][0]] = values
    return native, sorted(set(state) & set(allowed))


def convert_checkpoint(source_dir, output_dir):
    from .runtime import configure_runtime
    ms = configure_runtime("CPU")
    source, output = Path(source_dir), Path(output_dir)
    config = MessageConfig.from_json(source / "config.json")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Conversion output must be empty; existing artifacts are preserved")
    with np.load(source / "source_state.npz", allow_pickle=False) as state:
        native, discarded = map_numpy_state(state, config)
    # Some vocabulary entries are Unicode line separators. splitlines() would
    # change their token IDs; BERT vocabulary files are delimited by LF only.
    with (source / "vocab.txt").open(encoding="utf-8") as stream:
        vocabulary = [line.rstrip("\r\n") for line in stream]
    if len(vocabulary) != config.vocab_size or vocabulary[config.pad_token_id] != "[PAD]":
        raise ValueError("Source vocabulary/config mismatch")
    output.mkdir(parents=True, exist_ok=True)
    checkpoint = output / "model.ckpt"
    ms.save_checkpoint([{"name": name, "data": ms.Tensor(values)} for name, values in native.items()], str(checkpoint))
    config.save(output / "config.json")
    shutil.copyfile(source / "vocab.txt", output / "vocab.txt")
    provenance = json.loads((source / "provenance.json").read_text(encoding="utf-8"))
    manifest = {
        "format_version": 1, "framework": "mindspore", "checkpoint_type": "pretrained_encoder",
        "task": "pretraining", "model_id": "wisemessage-minirbt-h256-pretrained",
        "checkpoint": "model.ckpt", "config": "config.json", "vocab": "vocab.txt",
        "checkpoint_sha256": sha256_file(checkpoint), "config_fingerprint": config.fingerprint(),
        "tokenizer_sha256": sha256_file(output / "vocab.txt"),
        "source_checkpoint_sha256": sha256_file(source / "pytorch_model.bin"),
        "source": provenance, "converted_encoder_tensors": len(native),
        "encoder_parameters": sum(value.size for value in native.values()),
        "discarded_source_keys": discarded, "classifier_trained": False,
        "label_map": {"0": "normal", "1": "spam", "2": "scam"},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Only pretrained encoder. The three-class SMS head must be supervised-finetuned.",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", default="artifacts/sources/minirbt")
    parser.add_argument("--output-dir", default="artifacts/pretrained")
    args = parser.parse_args()
    print(json.dumps(convert_checkpoint(args.source_dir, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
