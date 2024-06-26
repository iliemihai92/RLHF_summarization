import json

import torch
from torch.utils.data import Dataset


class SFTDataset(Dataset):
    def __init__(self, path, tokenizer, split, max_length=512):
        self.input_train = []
        self.output_train = []
        self.input_val = []
        self.output_val = []
        self.split = split
        self.dataset = json.load(open(path, "r"))
        self.tokenizer = tokenizer
        self.max_length = max_length

        if "train" in split:
            for sample in self.dataset["train"]:
                self.input_train.append(sample["prompt"])
                self.output_train.append(sample["chosen"])
        elif "val" in split:
            for sample in self.dataset["val"]:
                self.input_val.append(sample["prompt"])
                self.output_val.append(sample["chosen"])

    def __len__(self):
        if "train" in self.split:
            return len(self.dataset["train"])
        elif "val" in self.split:
            return len(self.dataset["val"])

    def  __getitem__(self, idx):
        if "train" in self.split:
            txt_in = self.input_train[idx]
            txt_out = self.output_train[idx]
            encoding_dict = self.tokenizer(txt_in, truncation=True, max_length=self.max_length, padding="max_length")
            decoding_dict = self.tokenizer(txt_out, truncation=True, max_length=self.max_length, padding="max_length")

            return {
                "input_ids": torch.tensor(encoding_dict["input_ids"]),
                "attention_mask": torch.tensor(encoding_dict["attention_mask"]),
                "labels": torch.tensor(decoding_dict["input_ids"]),
                "decoder_attention_mask": torch.tensor(decoding_dict["attention_mask"])
            }

def my_collate(batch):

    input_batch = []
    attention_mask_batch = []
    labels_batch = []
    decoder_mask_batch = []
    for instance in batch:
        #print(instance["sentence1"])
        input_batch.append(instance["input_ids"])
        attention_mask_batch.append(instance["attention_mask"])
        labels_batch.append(instance["labels"])
        decoder_mask_batch.append(instance["decoder_attention_mask"])

    input_batch = torch.stack(input_batch)
    attention_mask_batch = torch.stack(attention_mask_batch)
    labels_batch = torch.stack(labels_batch)
    decoder_mask_batch = torch.stack(decoder_mask_batch)

    return input_batch, attention_mask_batch, labels_batch, decoder_mask_batch
