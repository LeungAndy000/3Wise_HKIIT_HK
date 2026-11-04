"""Equivalent export-only operations for the older end-side converter.

MindSpore 2.10 emits scalar Divs, absent from the 2.7.1 Lite registry. Materialize
the two compile-time reciprocals as float32 tensors and multiply instead. Every
parameter and the exact erf GELU formula remain the trained model's own.
"""
import math
import numpy as np
import mindspore as ms
from mindspore import nn, ops, Tensor
from wisemessage.model import BertSelfAttention, BertLayer, MessageClassifier


class PortableAttention(BertSelfAttention):
    def __init__(self, config):
        super().__init__(config)
        self.reciprocal_scale = Tensor(np.float32(1.0 / self.scale))

    def construct(self, hidden_states, additive_mask):
        query = self._split_heads(self.query(hidden_states))
        key = self._split_heads(self.key(hidden_states))
        value = self._split_heads(self.value(hidden_states))
        scores = self.query_key_matmul(query, key) * self.reciprocal_scale
        probabilities = self.dropout(ops.softmax(scores + additive_mask, axis=-1))
        context = self.batch_matmul(probabilities, value).transpose(0, 2, 1, 3)
        return context.reshape(hidden_states.shape[0], hidden_states.shape[1], self.hidden_size)


class PortableLayer(BertLayer):
    def __init__(self, config):
        super().__init__(config)
        self.attention = PortableAttention(config)
        self.reciprocal_sqrt_two = Tensor(np.float32(1.0 / math.sqrt(2.0)))

    def construct(self, hidden_states, additive_mask):
        attention = self.attention(hidden_states, additive_mask)
        attention = self.attention_dropout(self.attention_output(attention))
        attention = self.attention_layer_norm(hidden_states + attention)
        intermediate = self.intermediate(attention)
        intermediate = 0.5 * intermediate * (1.0 + ops.erf(intermediate * self.reciprocal_sqrt_two))
        output = self.output_dropout(self.output_dense(intermediate))
        return self.output_layer_norm(attention + output)


class PortableClassifier(MessageClassifier):
    def __init__(self, config):
        super().__init__(config)
        self.bert.layers = nn.CellList([PortableLayer(config) for _ in range(config.num_hidden_layers)])
        # Cell replacement happens after the parent's automatic prefixing.
        # Restore each full tree path before strict trained-weight loading.
        for name, parameter in self.parameters_and_names():
            parameter.name = name
