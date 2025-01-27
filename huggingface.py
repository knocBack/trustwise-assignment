import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from typing import Dict

from transformers import pipeline, AutoTokenizer

import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch.nn.functional

from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from transformers import pipeline, AutoTokenizer



def predict_vectara(text:str) -> float:
    model = AutoModelForSequenceClassification.from_pretrained(
        'vectara/hallucination_evaluation_model', trust_remote_code=True)
    text = [text.split('.')] # string to list[string]
    # print("text: ", text)
    result = model.predict(text)
    print(result)
    # print("type: ", type(result.item()))
    return round(result.item(), 3) # float type
    
def predict_vectara_v2(text:str) -> float:
    pairs = [ # Test data, List[Tuple[str, str]]
        ("I like you.","I love you"),
        # ("A man walks into a bar and buys a drink.", "A bloke swigs alcohol at a pub.")
    ]

    # Prompt the pairs
    # prompt = "<pad> Determine if the hypothesis is true given the premise?\n\nPremise: {text1}\n\nHypothesis: {text2}"
    prompt = "<pad> {text1} [SEP] {text2}"
    input_pairs = [prompt.format(text1=pair[0], text2=pair[1]) for pair in pairs]

    # Use text-classification pipeline to predict
    classifier = pipeline(
                "text-classification",
                model='vectara/hallucination_evaluation_model',
                tokenizer=AutoTokenizer.from_pretrained('google/flan-t5-base'),
                trust_remote_code=True
            )
    full_scores = classifier(input_pairs, top_k=None)
    print(full_scores)
    top_score = classifier(input_pairs, top_k=1) # top_k=1 means we only want the top 1 score w.r.t. the labels
    print(top_score)

    # Optional: Extract the scores for the 'consistent' label
    simple_scores = [score_dict['score'] for score_for_both_labels in full_scores for score_dict in score_for_both_labels if score_dict['label'] == 'consistent']

    print(simple_scores)
    # Expected output: [0.011061512865126133, 0.6473632454872131, 0.1290171593427658, 0.8969419002532959, 0.18462494015693665, 0.005031010136008263, 0.05432349815964699]
    return round(simple_scores[0], 3) # float type


from transformers import AutoModelForSequenceClassification, AutoTokenizer

def predict_vectara_v1(text:str) -> float:
    model = AutoModelForSequenceClassification.from_pretrained('vectara/hallucination_evaluation_model', trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base')

    inputs = tokenizer("A man walks into a bar and buys a drink [SEP] A bloke swigs alcohol at a pub", return_tensors='pt')
    # inputs = tokenizer("I like you [SEP] I love you", return_tensors='pt')
    outputs = model(**inputs)

    # Get the logits (tensor)
    logits = outputs.logits
    print(logits)

    scores = torch.nn.functional.softmax(logits, dim=1)
    print(scores)
    predicted_index = torch.argmax(scores, dim=1).item()
    print(predicted_index)
    predicted_prob = scores[0][predicted_index].item()
    print(predicted_prob)

    labels = model.config.id2label 
    print(labels)

    predicted_label = labels[predicted_index]
    print(predicted_label)

    scores = torch.sigmoid(logits)
    print(scores)

def predict_toxicity(text: str) -> float:
    tokenizer = RobertaTokenizer.from_pretrained('s-nlp/roberta_toxicity_classifier')
    model = RobertaForSequenceClassification.from_pretrained('s-nlp/roberta_toxicity_classifier')

    # batch = tokenizer.encode(text, return_tensors="pt")
    batch = tokenizer.encode(text, return_tensors="pt")

    output = model(batch)
    # idx 0 for neutral, idx 1 for toxic
    # print(output) -> logits = tensor([[idx0, idx1]], grad_fn=<AddmmBackward>)
    result = torch.nn.functional.softmax(output.logits) # The softmax function will normalize the logits for each class, ensuring that the probabilities sum up to 1.
    print(result)
    return round(result[0][1].item(),3) # idx 1 for toxic




def predict_emotion(text: str) -> Dict[str, float]:

    classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

    text = [text]
    # text = ["I hate you. I dislike you"]

    print(classifier(text))

    model_outputs = classifier(text, top_k=1) # top_k=1 means we only want the top 1 score w.r.t. the labels
    print(model_outputs)
    print(model_outputs[0])
    # produces a list of dicts for each of the labels
    result = model_outputs[0][0] # apply argmax to get the label with the highest probability TODO
    result['score'] = round(result['score'], 3)
    return result


def predict_gibberish(text: str) -> float:

    model = AutoModelForSequenceClassification.from_pretrained("wajidlinux99/gibberish-text-detector")

    tokenizer = AutoTokenizer.from_pretrained("wajidlinux99/gibberish-text-detector")

    # inputs = tokenizer("Is this text really worth it?", return_tensors="pt")
    inputs = tokenizer(text, return_tensors="pt")

    outputs = model(**inputs)
    print(outputs)
    # return outputs
    probs = torch.nn.functional.softmax(outputs.logits, dim=1) # outputs.logits tensor has shape (batch_size, num_classes)
                                                               # dim=1 means we want to apply softmax across the num_classes dimension or classes which are classified
                                                               # This means that the softmax function will normalize the logits for each class, ensuring that the probabilities sum up to 1.
    print(probs)

    predicted_index = torch.argmax(probs, dim=1).item() # probs tensor has shape (batch_size, num_classes), where batch_size is 1
                                                        # dim=1 means we want to apply argmax across the num_classes dimension or classes which are classified
                                                        # This means that the argmax function will return the index of the class with the highest probability.
    print(predicted_index)

    predicted_prob = probs[0][predicted_index].item() # This is the predicted probability for the chosen class.
    print(predicted_prob)

    labels = model.config.id2label 
    print(labels)

    predicted_label = labels[predicted_index]
    print(predicted_label)

    # for i, prob in enumerate(probs[0]):
    #     print(f"Class: {labels[i]}, Probability: {prob:.4f}")

    return {"label": predicted_label, "score": round(predicted_prob,3)}


def predict_education(text: str) -> float:
    tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/fineweb-edu-classifier")
    model = AutoModelForSequenceClassification.from_pretrained("HuggingFaceTB/fineweb-edu-classifier")

    inputs = tokenizer(text, return_tensors="pt", padding="longest", truncation=True)
    outputs = model(**inputs)
    # logits = outputs.logits.squeeze(-1).float()
    print(outputs)
    logits = outputs.logits
    probs = torch.nn.functional.softmax(logits, dim=-1)
    print(probs)
    probs = torch.sigmoid(logits)
    print(probs)
    score = probs[0][0].item()
    result = {
        "text": text,
        "score": round(score, 3)
    }

    return result
    


text = "I like you. I love you"
# text = "A man walks into a bar and buys a drink [SEP] A bloke swigs alcohol at a pub."
# print(predict_vectara(text))
# print(predict_vectara_v1(text))
# print(predict_vectara_v2(text))
# print(predict_toxicity(text)) # -5.201235294342041 -> 0.000 # DONE
# text2 = "I hate you. I dislike you"
# print(predict_toxicity(text2)) # 3.4832165241241455 -> 0.999
# text3 = "I dislike you"
# print(predict_toxicity(text3)) # 2.7813799381256104 -> 0.997
# print(predict_emotion(text))
# print(predict_gibberish(text)) # DONE
print(predict_education(text)) # DONE


# # Define the models and their corresponding tokenizers
# MODELS = {
#     "vectara": {
#         "model_name": "vectara/hallucination_evaluation_model",
#         "tokenizer_name": "google/flan-t5-base"
#     },
#     "toxicity": {
#         "model_name": "s-nlp/roberta_toxicity_classifier",
#         "tokenizer_name": "s-nlp/roberta_toxicity_classifier"
#     },
#     "emotion": {
#         "model_name": "SamLowe/roberta-base-go-emotions",
#         "tokenizer_name": "SamLowe/roberta-base-go-emotions"
#     },
#     "gibberish": {
#         "model_name": "wajidlinux99/gibberish-text-detector",
#         "tokenizer_name": "wajidlinux99/gibberish-text-detector"
#     },
#     "education": {
#         "model_name": "HuggingFaceFW/fineweb-edu-classifier",
#         "tokenizer_name": "HuggingFaceFW/fineweb-edu-classifier"
#     }
# }

# # Load the models and tokenizers
# models = {}
# model_name = "vectara"
# model_info = MODELS[model_name]
# models[model_name] = {
#     "model": AutoModelForSequenceClassification.from_pretrained(model_info["model_name"], trust_remote_code=True),
#     "tokenizer": AutoTokenizer.from_pretrained(model_info["tokenizer_name"])
# }

# def predict_vectara_old(text: str) -> float:
#     """Predict the hallucination score using the Vectara model."""
#     inputs = models["vectara"]["tokenizer"](text, return_tensors="pt")
#     outputs = models["vectara"]["model"](**inputs)
#     print(outputs)
#     print(torch.nn.functional.softmax(outputs.logits, dim=1))
#     print(torch.sigmoid(outputs.logits))
#     labels = models["vectara"]["model"].config.id2label 
#     print(labels)
#     return torch.nn.functional.softmax(outputs.logits, dim=1).detach().numpy()[0][1]

# # print(predict_vectara_old("I like you. [SEP] I love you"))
# print(predict_vectara_old("A man walks into a bar and buys a drink [SEP] A bloke swigs alcohol at a pub."))