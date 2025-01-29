import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from typing import Dict
from transformers import RobertaTokenizer, RobertaForSequenceClassification

def predict_vectara_old(text:str) -> float:
    model = AutoModelForSequenceClassification.from_pretrained(
        'vectara/hallucination_evaluation_model', trust_remote_code=True)
    text = [text.split('.',2)] # string to list[string]
    # print("text: ", text)
    result = model.predict(text)
    print(result)
    # print("type: ", type(result.item()))
    return round(result.item(), 3) # float type
    
def predict_vectara(text:str) -> float:
    pairs = [ tuple(text.rsplit('[SEP]', 2)) if len(text.rsplit('[SEP]',2))==2 else (text, "") ] # string to tuple(string, string)

    # Prompt the pairs
    prompt = "<pad> Determine if the hypothesis is true given the premise?\n\nPremise: {text1}\n\nHypothesis: {text2}"
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

    result = [score['score'] for score in full_scores[0] if score['label']=='consistent']
    print(result)
    return round(result[0], 3) # float {:0.3f}


def predict_vectara_v1(text:str) -> float:
    model = AutoModelForSequenceClassification.from_pretrained('vectara/hallucination_evaluation_model', trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base')

    # inputs = tokenizer("A man walks into a bar and buys a drink [SEP] A bloke swigs alcohol at a pub", return_tensors='pt')
    inputs = tokenizer(text, return_tensors='pt')
    outputs = model(**inputs)

    # Get the logits (tensor)
    logits = outputs.logits
    # print(logits)

    scores = torch.nn.functional.softmax(logits, dim=1)
    # print(scores)
    predicted_index = torch.argmax(scores, dim=1).item()
    # print(predicted_index)
    predicted_prob = scores[0][predicted_index].item()
    # print(predicted_prob)

    labels = model.config.id2label 
    # print(labels)

    predicted_label = labels[predicted_index]
    # print(predicted_label)

    scores = torch.sigmoid(logits)
    # print(scores)
    return scores[0][0].item()

def predict_toxicity(text: str) -> float:
    tokenizer = RobertaTokenizer.from_pretrained('s-nlp/roberta_toxicity_classifier')
    model = RobertaForSequenceClassification.from_pretrained('s-nlp/roberta_toxicity_classifier')

    # batch = tokenizer.encode(text, return_tensors="pt")
    batch = tokenizer.encode(text, return_tensors="pt")

    output = model(batch)  # logits -> idx 0 for neutral, idx 1 for toxic
    # print(output) # -> logits = tensor([[idx0, idx1]], grad_fn=<AddmmBackward>)
    result = torch.nn.functional.softmax(output.logits, dim=1) # The softmax function will normalize the logits for each class, ensuring that the probabilities sum up to 1.
    # print(result)
    result = result[0] # first tensor in the batch
    return round(result[1].item(),3) # idx 1 for toxic




def predict_emotion(text: str) -> Dict[str, float]:

    classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

    text = [text]
    # text = ["I hate you. I dislike you"]

    # print(classifier(text))

    model_outputs = classifier(text, top_k=1) # top_k=1 means we only want the top 1 score w.r.t. the labels
    # print(model_outputs)
    # print(model_outputs[0])
    # produces a list of dicts for each of the labels
    result = model_outputs[0][0]
    result['score'] = round(result['score'], 3) # {'label': 'clean', 'score': 0.873}
    return result


def predict_gibberish(text: str) -> Dict[str, float]:

    model = AutoModelForSequenceClassification.from_pretrained("wajidlinux99/gibberish-text-detector")

    tokenizer = AutoTokenizer.from_pretrained("wajidlinux99/gibberish-text-detector")

    # inputs = tokenizer("Is this text really worth it?", return_tensors="pt")
    inputs = tokenizer(text, return_tensors="pt")

    outputs = model(**inputs)
    # print(outputs)
    # return outputs
    probs = torch.nn.functional.softmax(outputs.logits, dim=1) # outputs.logits tensor has shape (batch_size, num_classes)
                                                               # dim=1 means we want to apply softmax across the num_classes dimension or classes which are classified
                                                               # This means that the softmax function will normalize the logits for each class, ensuring that the probabilities sum up to 1.
    # print(probs)

    predicted_index = torch.argmax(probs, dim=1).item() # probs tensor has shape (batch_size, num_classes), where batch_size is 1
                                                        # dim=1 means we want to apply argmax across the num_classes dimension or classes which are classified
                                                        # This means that the argmax function will return the index of the class with the highest probability.
    # print(predicted_index)

    predicted_prob = probs[0][predicted_index].item() # This is the predicted probability for the chosen class.
    # print(predicted_prob)

    labels = model.config.id2label 
    # print(labels)

    predicted_label = labels[predicted_index]
    # print(predicted_label)

    # for i, prob in enumerate(probs[0]):
    #     print(f"Class: {labels[i]}, Probability: {prob:.4f}")

    return {"label": predicted_label, "score": round(predicted_prob,3)}


def predict_education(text: str) -> float:
    tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/fineweb-edu-classifier")
    model = AutoModelForSequenceClassification.from_pretrained("HuggingFaceTB/fineweb-edu-classifier")

    inputs = tokenizer(text, return_tensors="pt", padding="longest", truncation=True)
    outputs = model(**inputs)
    # logits = outputs.logits.squeeze(-1).float()
    # print(outputs)
    logits = outputs.logits
    # probs = torch.nn.functional.softmax(logits, dim=-1)
    # print(probs)
    probs = torch.sigmoid(logits)
    # print(probs)
    score = probs[0][0].item()
    score = round(score, 3)
    # result = {
    #     "text": text,
    #     "score": score
    # }

    return score
    

if __name__ == "__main__":
    text = "I hate you, you are disliked"
    # text = "A man walks into a bar and buys a drink [SEP] A bloke swigs alcohol at a pub."
    print(predict_vectara(text))
    # print(predict_vectara_v1(text))
    # print(predict_vectara_old(text))
    # print(predict_toxicity(text)) # -5.~201235294342041 -> 0.000 # DONE
    # text2 = "I hate you. I dislike you"
    # print(predict_toxicity(text2)) # 3.4832165241241455 -> 0.999
    # text3 = "I dislike you"
    # print(predict_toxicity(text3)) # 2.7813799381256104 -> 0.997
    # print(predict_emotion(text)) # DONE
    # print(predict_gibberish(text)) # DONE
    # print(predict_education(text)) # DONE

