# Tokenize sentences using BERT tokenizer

from transformers import BertConfig, BertTokenizer
from doc2txt.utils.bert_config import Config

config = Config()

def tokenize_sentence(sentence):
    tokenizer = BertTokenizer.from_pretrained(config.bert_model_name, do_lower_case=True)
    text_ids = tokenizer.encode(sentence,
                                add_special_tokens=True,
                                truncation=True,
                                max_length=128)
    pad_num = 128 - len(text_ids)
    attn_mask = [1] * len(text_ids) + [0] * pad_num
    text_ids = text_ids + [0] * pad_num
    return [text_ids, attn_mask]
