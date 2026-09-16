import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
import joblib

# =========================
# 1. Load training data
# =========================

DATA_PATH = r"data\training_data.csv"
MODEL_PATH = r"data\xgboost_landslide_model_no_location.pkl"

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)

# =========================
# 2. Features WITHOUT location
# =========================

features = [
    "elevation",
    "slope",
    "aspect",
    "B2",
    "B3",
    "B4",
    "B5",
    "NDVI",
    "NDWI",
    "NBR"
]

target = "label"

X = df[features]
y = df[target]

# =========================
# 3. Handle missing values
# =========================

imputer = SimpleImputer(strategy="median")

X = pd.DataFrame(
    imputer.fit_transform(X),
    columns=features
)

# =========================
# 4. Train / test split
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples :", len(X_test))

# =========================
# 5. XGBoost model
# =========================

model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42
)

# =========================
# 6. Train
# =========================

print("\nTraining XGBoost...")

model.fit(X_train, y_train)

# =========================
# 7. Predictions
# =========================

y_pred = model.predict(X_test)

# =========================
# 8. Evaluation
# =========================

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n===== MODEL PERFORMANCE =====")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

print("\n===== CLASSIFICATION REPORT =====")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Non-Landslide", "Landslide"]
    )
)

print("\n===== CONFUSION MATRIX =====")
print(confusion_matrix(y_test, y_pred))

# =========================
# 9. Feature importance
# =========================

importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print("\n===== FEATURE IMPORTANCE =====")
print(importance)

# =========================
# 10. Save model
# =========================

joblib.dump(
    {
        "model": model,
        "imputer": imputer,
        "features": features
    },
    MODEL_PATH
)

print("\nModel saved successfully!")
print("Output:", MODEL_PATH)