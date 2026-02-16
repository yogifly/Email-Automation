import joblib
import os

# Load models once on startup
MODEL_PATH = "app/ml_models"

spam_model = joblib.load(os.path.join(MODEL_PATH, "model_spam_ham.pkl"))
priority_model = joblib.load(os.path.join(MODEL_PATH, "model_priority.pkl"))
shared_vectorizer = joblib.load(os.path.join(MODEL_PATH, "email-vectorizer.pkl"))
subject_model = joblib.load(os.path.join(MODEL_PATH, "stacked_email_classifier.joblib"))
subject_vectorizer = joblib.load(os.path.join(MODEL_PATH, "tfidf_vectorizer.joblib"))

def predict_spam(text):
    X = shared_vectorizer.transform([text])
    return spam_model.predict(X)[0]           

def predict_priority(text: str):
    X = shared_vectorizer.transform([text])
    return priority_model.predict(X)[0]

def predict_subject(text: str):
    return subject_model.predict([text])[0]   
