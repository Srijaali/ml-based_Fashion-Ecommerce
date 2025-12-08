import joblib
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class SentimentModels:
    def __init__(self):
        # Load DistilBERT model
        self.tokenizer = AutoTokenizer.from_pretrained("models/sentiment/distilbert")
        self.bert_model = AutoModelForSequenceClassification.from_pretrained(
            "models/sentiment/distilbert"
        )

        # Load TF-IDF baseline models
        self.lr = joblib.load("models/sentiment/lr_tfidf.joblib")
        self.svm = joblib.load("models/sentiment/svm_tfidf.joblib")
        self.nb = joblib.load("models/sentiment/nb_tfidf.joblib")

        # Load vectorizer
        self.vectorizer = joblib.load("models/sentiment/reviews_tfidf_vectorizer.pkl")

    def predict_bert(self, text):
        tokens = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            output = self.bert_model(**tokens)
            probs = torch.softmax(output.logits, dim=1)[0].tolist()

        labels = ["negative", "neutral", "positive"]
        pred = labels[probs.index(max(probs))]

        return {
            "label": pred,
            "scores": {
                "negative": probs[0],
                "neutral": probs[1],
                "positive": probs[2]
            }
        }

    def predict_tfidf(self, text):
        vec = self.vectorizer.transform([text])
        lr_pred = self.lr.predict(vec)[0]
        svm_pred = self.svm.predict(vec)[0]
        nb_pred = self.nb.predict(vec)[0]

        return {
            "lr": lr_pred,
            "svm": svm_pred,
            "nb": nb_pred
        }

sentiment_models = SentimentModels()
