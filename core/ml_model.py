import joblib
import pandas as pd
import os
from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR, "safe_model.pkl")

model = joblib.load(MODEL_PATH)

def predict_severity(age, bmi, symptoms, heart_history):

    feature_order = [
        "age","bmi","heart_history",
        "chest_pain","shortness_of_breath","fever","cough","cold",
        "headache","nausea","dizziness","fatigue","vomiting"
    ]

    features = dict.fromkeys(feature_order, 0)

    features["age"] = age
    features["bmi"] = bmi
    features["heart_history"] = int(heart_history)

    for s in symptoms:
        key = s.replace(" ", "_")
        if key in features:
            features[key] = 1

    X = pd.DataFrame([features])

    prediction = model.predict(X)[0]

    return prediction