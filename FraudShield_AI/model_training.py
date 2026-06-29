import os
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

os.makedirs("models", exist_ok=True)

DATA_PATH = "data/telecom_fraud.csv"
MODEL_PATH = "models/xgboost_model.pkl"
FEATURES_PATH = "models/features.pkl"

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError("Dataset not found. Run: python generate_dataset.py")

df = pd.read_csv(DATA_PATH)
X = df.drop(["customer_id", "fraud_label"], axis=1)
y = df["fraud_label"]
features = list(X.columns)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = XGBClassifier(
    n_estimators=350,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.85,
    colsample_bytree=0.85,
    eval_metric="logloss",
    random_state=42,
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, predictions))
print("\nClassification Report:")
print(classification_report(y_test, predictions))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

joblib.dump(model, MODEL_PATH)
joblib.dump(features, FEATURES_PATH)

print("\nModel saved successfully.")
print("Saved:", MODEL_PATH)
print("Saved:", FEATURES_PATH)
