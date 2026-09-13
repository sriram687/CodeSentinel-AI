import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
TOKENIZER_DIR = os.path.join(BASE_DIR, "tokenizer")

VOCAB_PATH = os.path.join(TOKENIZER_DIR, "drapgh-vocab.json")
MERGES_PATH = os.path.join(TOKENIZER_DIR, "drapgh-merges.txt")

MAX_SEQ_LENGTH = 1024
DEFAULT_DEVICE = "cuda"

DATASETS = ["draper", "devign", "mvd", "reveal", "vuldeepecker", "d2a"]
