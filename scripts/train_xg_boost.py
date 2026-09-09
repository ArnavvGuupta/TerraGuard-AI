import os
import joblib
import pandas as pd

from xgboost import XGBClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# PATHS
# ============================================================

DATA_PATH = r"data\training_data.csv"
MODEL_PATH = r"data\xgboost_landslide_model.pkl"


# ============================================================
# 1. LOAD DATASET
# ============================================================

print("Loading training dataset...")

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# 2. HANDLE MISSING VALUES
# ============================================================

print("\nMissing values before preprocessing:")

print(df.isnull().sum())


# Replace missing spectral values with column median
# This keeps all 480 samples.

feature_columns = [
    "elevation",
    "slope",
    "aspect",
    "B2",
    "B3",
    "B4",
    "B5",
    "NDVI",
    "NDWI",
    "NBR",
    "latitude",
    "longitude"
]

df[feature_columns] = df[feature_columns].fillna(
    df[feature_columns].median()
)


print("\nMissing values after preprocessing:")

print(df[feature_columns].isnull().sum())


# ============================================================
# 3. CREATE X AND y
# ============================================================

X = df[feature_columns]

y = df["label"]


print("\nFeatures used for training:")

print(feature_columns)

print("\nX shape:", X.shape)
print("y shape:", y.shape)


# ============================================================
# 4. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# 5. CREATE XGBOOST MODEL
# ============================================================

print("\nCreating XGBoost model...")

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


# ============================================================
# 6. TRAIN MODEL
# ============================================================

print("\nTraining XGBoost...")

model.fit(
    X_train,
    y_train
)

print("Training completed successfully!")


# ============================================================
# 7. PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 8. MODEL EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred
)

recall = recall_score(
    y_test,
    y_pred
)

f1 = f1_score(
    y_test,
    y_pred
)


print("\n===================================")
print("       XGBOOST MODEL RESULTS")
print("===================================")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")


# ============================================================
# 9. CLASSIFICATION REPORT
# ============================================================

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
# 10. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\nConfusion Matrix:")

print(cm)


# ============================================================
# 11. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "feature": feature_columns,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    by="importance",
    ascending=False
)

print("\nFeature Importance:")

print(importance.to_string(index=False))


# ============================================================
# 12. SAVE MODEL
# ============================================================

os.makedirs(
    os.path.dirname(MODEL_PATH),
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)

print("\nModel saved to:")

print(
    os.path.abspath(MODEL_PATH)
)