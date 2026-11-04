"""Native MindSpore MiniRBT encoder and Chinese SMS three-class classifier.

There is deliberately no Hugging Face/PyTorch dependency in this module. The
encoder follows BertForMaskedLM's backbone without a pooler or the MLM head.
"""

import math

import mindspore as ms
from mindspore import Tensor, nn, ops
from mindspore.common.initializer import Normal
import numpy as np

from .config import MessageConfig


def _dense(in_features, out_features, config):
    return nn.Dense(in_features, out_features,
                    weight_init=Normal(config.initializer_range), bias_init="zeros")


class BertEmbeddings(nn.Cell):
    def __init__(self, config):
        super().__init__()
        init = Normal(config.initializer_range)
        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size,
                                            embedding_table=init)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size,
                                                embedding_table=init)
        self.token_type_embeddings = nn.Embedding(config.type_vocab_size, config.hidden_size,
                                                  embedding_table=init)
        self.layer_norm = nn.LayerNorm((config.hidden_size,), epsilon=config.layer_norm_eps)
        self.dropout = nn.Dropout(p=config.hidden_dropout_prob)
        self.position_ids = Tensor(np.arange(config.max_position_embeddings)[None, :], ms.int32)

    def construct(self, input_ids, token_type_ids):
        length = input_ids.shape[1]
        embeddings = (self.word_embeddings(input_ids)
                      + self.token_type_embeddings(token_type_ids)
                      + self.position_embeddings(self.position_ids[:, :length]))
        return self.dropout(self.layer_norm(embeddings))


class BertSelfAttention(nn.Cell):
    def __init__(self, config):
        super().__init__()
        self.num_heads = config.num_attention_heads
        self.head_size = config.hidden_size // self.num_heads
        self.hidden_size = config.hidden_size
        self.scale = math.sqrt(self.head_size)
        self.query = _dense(config.hidden_size, config.hidden_size, config)
        self.key = _dense(config.hidden_size, config.hidden_size, config)
        self.value = _dense(config.hidden_size, config.hidden_size, config)
        self.dropout = nn.Dropout(p=config.attention_probs_dropout_prob)
        self.batch_matmul = ops.BatchMatMul()
        self.query_key_matmul = ops.BatchMatMul(transpose_b=True)

    def _split_heads(self, values):
        batch, length, _ = values.shape
        return values.reshape(batch, length, self.num_heads, self.head_size).transpose(0, 2, 1, 3)

    def construct(self, hidden_states, additive_mask):
        query = self._split_heads(self.query(hidden_states))
        key = self._split_heads(self.key(hidden_states))
        value = self._split_heads(self.value(hidden_states))
        scores = self.query_key_matmul(query, key) / self.scale
        probabilities = self.dropout(ops.softmax(scores + additive_mask, axis=-1))
        context = self.batch_matmul(probabilities, value).transpose(0, 2, 1, 3)
        return context.reshape(hidden_states.shape[0], hidden_states.shape[1], self.hidden_size)


class BertLayer(nn.Cell):
    def __init__(self, config):
        super().__init__()
        self.attention = BertSelfAttention(config)
        self.attention_output = _dense(config.hidden_size, config.hidden_size, config)
        self.attention_dropout = nn.Dropout(p=config.hidden_dropout_prob)
        self.attention_layer_norm = nn.LayerNorm((config.hidden_size,), epsilon=config.layer_norm_eps)
        self.intermediate = _dense(config.hidden_size, config.intermediate_size, config)
        self.output_dense = _dense(config.intermediate_size, config.hidden_size, config)
        self.output_dropout = nn.Dropout(p=config.hidden_dropout_prob)
        self.output_layer_norm = nn.LayerNorm((config.hidden_size,), epsilon=config.layer_norm_eps)
        self.sqrt_two = math.sqrt(2.0)

    def construct(self, hidden_states, additive_mask):
        attention = self.attention(hidden_states, additive_mask)
        attention = self.attention_dropout(self.attention_output(attention))
        attention = self.attention_layer_norm(hidden_states + attention)
        intermediate = self.intermediate(attention)
        # Hugging Face's `gelu` is the exact erf version. MindSpore nn.GELU
        # defaults to an approximation, so spell out the exact baseline here.
        intermediate = 0.5 * intermediate * (1.0 + ops.erf(intermediate / self.sqrt_two))
        output = self.output_dropout(self.output_dense(intermediate))
        return self.output_layer_norm(attention + output)


class BertEncoder(nn.Cell):
    """The MiniRBT encoder, returning [batch, sequence, hidden]."""

    def __init__(self, config: MessageConfig):
        super().__init__()
        self.embeddings = BertEmbeddings(config)
        self.layers = nn.CellList([BertLayer(config) for _ in range(config.num_hidden_layers)])
        self.max_positions = config.max_position_embeddings

    def construct(self, input_ids, attention_mask, token_type_ids=None):
        if input_ids.shape[1] > self.max_positions:
            raise ValueError("Input exceeds max_position_embeddings")
        if token_type_ids is None:
            token_type_ids = ops.zeros_like(input_ids)
        hidden_states = self.embeddings(input_ids, token_type_ids)
        mask = ops.cast(attention_mask[:, None, None, :], hidden_states.dtype)
        additive_mask = (1.0 - mask) * -3.4028234663852886e38
        for layer in self.layers:
            hidden_states = layer(hidden_states, additive_mask)
        return hidden_states


class MessageClassifier(nn.Cell):
    """MiniRBT CLS -> dropout -> linear(hidden_size, 3)."""

    def __init__(self, config: MessageConfig):
        super().__init__()
        self.bert = BertEncoder(config)
        self.dropout = nn.Dropout(p=config.classifier_dropout_prob)
        self.classifier = _dense(config.hidden_size, config.num_labels, config)

    def construct(self, input_ids, attention_mask, token_type_ids=None):
        sequence = self.bert(input_ids, attention_mask, token_type_ids)
        return self.classifier(self.dropout(sequence[:, 0, :]))
