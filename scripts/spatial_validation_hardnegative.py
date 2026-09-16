import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from sklearn.impute import SimpleImputer

from xgboost import XGBClassifier


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "training_data_hard_negative.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("SPATIAL VALIDATION - HARD NEGATIVE DATASET")
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
# SPATIAL ZONES
# ============================================================

# Divide longitude into three geographic zones.
#
# West + Central = training
# East = testing
#
# Latitude/longitude are NOT used as ML features.

q1 = df["longitude"].quantile(1 / 3)
q2 = df["longitude"].quantile(2 / 3)

df["spatial_zone"] = pd.cut(
    df["longitude"],
    bins=[
        -np.inf,
        q1,
        q2,
        np.inf
    ],
    labels=[
        "West",
        "Central",
        "East"
    ]
)


print("\nSpatial zone distribution:")
print(
    df.groupby(
        ["spatial_zone", "label"],
        observed=False
    ).size()
)


# ============================================================
# TRAIN / TEST MASK
# ============================================================

train_mask = df["spatial_zone"].isin(
    ["West", "Central"]
)

test_mask = df["spatial_zone"] == "East"


X_train = df.loc[train_mask, features]
y_train = df.loc[train_mask, "label"]

X_test = df.loc[test_mask, features]
y_test = df.loc[test_mask, "label"]


print("\nSpatial split:")
print(
    "Training zones: West + Central"
)

print(
    "Testing zone : East"
)

print(
    f"Training samples: {len(X_train)}"
)

print(
    f"Testing samples : {len(X_test)}"
)


# ============================================================
# IMPUTATION
# ============================================================

imputer = SimpleImputer(
    strategy="median"
)

X_train = imputer.fit_transform(X_train)
X_test = imputer.transform(X_test)


# ============================================================
# XGBOOST
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

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)


print("\n" + "=" * 60)
print("SPATIAL VALIDATION RESULTS")
print("=" * 60)

print(
    f"\nAccuracy : {accuracy:.4f}"
)

print(
    f"Precision: {precision:.4f}"
)

print(
    f"Recall   : {recall:.4f}"
)

print(
    f"F1 Score : {f1:.4f}"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Non-Landslide",
            "Landslide"
        ],
        zero_division=0
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
# ADDITIONAL SPATIAL INFORMATION
# ============================================================

print("\nTest region information:")

print(
    f"Longitude range: "
    f"{df.loc[test_mask, 'longitude'].min():.6f}"
    f" - "
    f"{df.loc[test_mask, 'longitude'].max():.6f}"
)

print(
    f"Latitude range: "
    f"{df.loc[test_mask, 'latitude'].min():.6f}"
    f" - "
    f"{df.loc[test_mask, 'latitude'].max():.6f}"
)


print("\nDone.")