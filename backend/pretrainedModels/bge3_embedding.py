from transformers import AutoTokenizer, AutoModel
import torch


class SingletonModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonModel, cls).__new__(cls)
            cls._instance.tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
            cls._instance.model = AutoModel.from_pretrained("BAAI/bge-m3").to(
                'cuda' if torch.cuda.is_available() else 'cpu')
        return cls._instance