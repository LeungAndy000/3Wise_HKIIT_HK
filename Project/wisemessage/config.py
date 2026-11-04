"""Standalone MiniRBT configuration for three-way Chinese SMS classification."""

from dataclasses import asdict, dataclass, fields
import hashlib
import json
from pathlib import Path


LABELS = {0: "normal", 1: "spam", 2: "scam"}


@dataclass(frozen=True)
class MessageConfig:
    vocab_size: int = 21128
    hidden_size: int = 256
    num_hidden_layers: int = 6
    num_attention_heads: int = 8
    intermediate_size: int = 1024
    max_position_embeddings: int = 512
    type_vocab_size: int = 2
    hidden_dropout_prob: float = 0.1
    attention_probs_dropout_prob: float = 0.1
    classifier_dropout_prob: float = 0.1
    layer_norm_eps: float = 1e-12
    initializer_range: float = 0.02
    pad_token_id: int = 0
    hidden_act: str = "gelu"
    num_labels: int = 3

    def __post_init__(self):
        for name in ("vocab_size", "hidden_size", "num_hidden_layers", "num_attention_heads",
                     "intermediate_size", "max_position_embeddings", "type_vocab_size"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.hidden_size % self.num_attention_heads:
            raise ValueError("hidden_size must be divisible by num_attention_heads")
        if self.hidden_act != "gelu":
            raise ValueError("Only exact GELU is supported")
        if self.num_labels != 3:
            raise ValueError("WiseMessage requires normal, spam and scam labels")
        if not 0 <= self.pad_token_id < self.vocab_size:
            raise ValueError("pad_token_id must be inside the vocabulary")
        for name in ("hidden_dropout_prob", "attention_probs_dropout_prob", "classifier_dropout_prob"):
            if not 0 <= getattr(self, name) < 1:
                raise ValueError(f"{name} must be in [0, 1)")
        if self.layer_norm_eps <= 0 or self.initializer_range <= 0:
            raise ValueError("Layer norm epsilon and initializer range must be positive")

    @classmethod
    def from_dict(cls, values):
        if values.get("model_type", "bert") != "bert":
            raise ValueError("Expected a BERT/MiniRBT checkpoint")
        if values.get("position_embedding_type", "absolute") != "absolute":
            raise ValueError("Only absolute position embeddings are supported")
        if values.get("is_decoder", False) or values.get("add_cross_attention", False):
            raise ValueError("Decoder and cross-attention models are unsupported")
        names = {field.name for field in fields(cls)}
        return cls(**{key: value for key, value in values.items() if key in names})

    @classmethod
    def from_json(cls, path):
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8-sig")))

    def to_dict(self):
        return asdict(self)

    def fingerprint(self):
        content = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def save(self, path):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")


Config = MessageConfig
