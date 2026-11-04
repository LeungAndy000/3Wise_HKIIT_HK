"""MiniRBT's own Chinese BERT WordPiece preprocessing, with zero segment IDs."""

from pathlib import Path
import numpy as np


class MessageTokenizer:
    def __init__(self, vocab_path, max_length=128, do_lower_case=True):
        if isinstance(max_length, bool) or not isinstance(max_length, int) or max_length < 2:
            raise ValueError("max_length must be an integer >= 2")
        from tokenizers import BertWordPieceTokenizer
        self.vocab_path = Path(vocab_path)
        self.max_length = max_length
        self.pad_size = max_length
        self.do_lower_case = do_lower_case
        self._tokenizer = BertWordPieceTokenizer(
            str(self.vocab_path), lowercase=do_lower_case, strip_accents=None,
            clean_text=True, handle_chinese_chars=True,
        )
        self._tokenizer.enable_truncation(max_length=max_length)
        special = {key: self._tokenizer.token_to_id(key)
                   for key in ("[PAD]", "[CLS]", "[SEP]", "[UNK]", "[MASK]")}
        if any(value is None for value in special.values()):
            raise ValueError("MiniRBT vocabulary lacks mandatory special tokens")
        self.pad_token_id = special["[PAD]"]
        self.cls_token_id = special["[CLS]"]
        self.sep_token_id = special["[SEP]"]
        self.vocab_size = self._tokenizer.get_vocab_size()
        self._tokenizer.enable_padding(length=max_length, pad_id=self.pad_token_id, pad_token="[PAD]")

    def encode_batch(self, texts):
        texts = list(texts)
        if not all(isinstance(text, str) for text in texts):
            raise TypeError("Messages must be strings")
        encodings = self._tokenizer.encode_batch(texts)
        if not encodings:
            return {key: np.empty((0, self.max_length), dtype=np.int32)
                    for key in ("input_ids", "attention_mask", "token_type_ids")}
        ids = np.asarray([item.ids for item in encodings], dtype=np.int32)
        masks = np.asarray([item.attention_mask for item in encodings], dtype=np.int32)
        return {"input_ids": ids, "attention_mask": masks, "token_type_ids": np.zeros_like(ids)}

    def encode(self, text):
        return {key: values[0].tolist() for key, values in self.encode_batch([text]).items()}

    __call__ = encode_batch
