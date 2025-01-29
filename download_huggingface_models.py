import logging
from transformers import AutoModel, AutoTokenizer

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

model_names = [
    's-nlp/roberta_toxicity_classifier',
    "SamLowe/roberta-base-go_emotions",
    "wajidlinux99/gibberish-text-detector",
    "HuggingFaceTB/fineweb-edu-classifier"
]


def download_models():
    for model_name in model_names:
        logging.debug(f"Downloading model: {model_name}")
        model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        logging.debug(f"Model and tokenizer for '{model_name}' downloaded.")

if __name__ == "__main__":
    download_models()
