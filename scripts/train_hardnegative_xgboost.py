import pandas as pd
import numpy as np
import joblib

from pathlib import Path

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

from xgboost import XGBClassifier


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "training_data_hard_negative.csv"

MODEL_PATH = BASE_DIR / "data" / "xgboost_landslide_model_hard_negative.pkl"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("HARD-NEGATIVE XGBOOST TRAINING")
print("=" * 60)

print(f"\nDataset: {DATA_PATH}")
print(f"Shape: {df.shape}")

print("\nClass distribution:")
print(df["label"].value_counts())


# ============================================================
# FEATURES
# ============================================================

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

X = df[features]
y = df["label"]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples :", len(X_test))


# ============================================================
# IMPUTATION
# ============================================================

imputer = SimpleImputer(strategy="median")

X_train = imputer.fit_transform(X_train)
X_test = imputer.transform(X_test)


# ============================================================
# XGBOOST MODEL
# ============================================================

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


print("\nTraining XGBoost...")

model.fit(
    X_train,
    y_train
)


# ============================================================
# PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)


print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

print(f"\nAccuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")


print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Non-Landslide",
            "Landslide"
        ]
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")

cm = confusion_matrix(
    y_test,
    y_pred
)

print(cm)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

print("\nFeature Importance:")

for _, row in importance.iterrows():
    print(
        f"{row['Feature']:10s} : "
        f"{row['Importance']:.6f}"
    )


# ============================================================
# SAVE MODEL + IMPUTER
# ============================================================

artifact = {
    "model": model,
    "imputer": imputer,
    "features": features
}

joblib.dump(
    artifact,
    MODEL_PATH
)


print("\n" + "=" * 60)
print("MODEL SAVED")
print("=" * 60)

print(MODEL_PATH)

print("\nDone.")