# -*- coding: utf-8 -*-

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer
import csv
"""
数据加载
"""


class DataGenerator:
    def __init__(self, path: str, config):
        self.path = path
        self.config = config
        self.config["class_num"] = 2
        if self.config["model_type"] == "bert":
            self.tokenizer = BertTokenizer.from_pretrained(config["pretrain_model_path"])
        self.vocab = load_vocab(config["vocab_path"])
        self.config["vocab_size"] = len(self.vocab)
        self.load()


    def load(self):
        self.data = []
        with open(self.path, 'r',encoding="utf8") as f:
            csv_reader = csv.reader(f)
            next(csv_reader)
            for line in csv_reader:
                x_sentence = line[1]
                y_sentence = line[0]
                # print("x_sentence:", x_sentence, "y_sentence:", y_sentence)
                if self.config["model_type"] == "bert":
                    x_indexes = self.tokenizer.encode(x_sentence, max_length=self.config["max_length"], pad_to_max_length=True)
                else:
                    x_indexes = self.encode_sentence(x_sentence)
                x_indexes = torch.LongTensor(x_indexes)
                y_index = torch.LongTensor([int(y_sentence)])
                self.data.append([x_indexes, y_index])
        return

    def encode_sentence(self, text):
        input_id = []
        for char in text:
            input_id.append(self.vocab.get(char, self.vocab["[UNK]"]))
        input_id = self.padding(input_id)
        return input_id

    #补齐或截断输入的序列，使其可以在一个batch内运算
    def padding(self, input_id):
        input_id = input_id[:self.config["max_length"]]
        input_id += [0] * (self.config["max_length"] - len(input_id))
        return input_id

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

# 加载词表
def load_vocab(vocab_path):
    token_dict = {}
    with open(vocab_path, encoding="utf8") as f:
        for index, line in enumerate(f):
            token = line.strip()
            token_dict[token] = index + 1  #0留给padding位置，所以从1开始
    return token_dict


#用torch自带的DataLoader类封装数据
def load_data(data_path, config, shuffle=True):
    dg = DataGenerator(data_path, config)
    dl = DataLoader(dg, batch_size=config["batch_size"], shuffle=shuffle)
    return dl

if __name__ == "__main__":
    from config import Config
    dg = DataGenerator(Config["valid_data_path"], Config)
    print(dg[1])
