import pandas as pd
import numpy as np

from xgboost import XGBClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# ==========================================
# 1. Load dataset
# ==========================================

DATA_PATH = r"data\training_data.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)

# ==========================================
# 2. Features
# ==========================================

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

# ==========================================
# 3. Create geographic regions
# ==========================================
#
# Instead of randomly splitting individual
# points, divide the study area into geographic
# longitude zones.
#
# Left/middle/right regions are kept separate.
# ==========================================

longitude = df["longitude"]

q1 = longitude.quantile(0.33)
q2 = longitude.quantile(0.66)

df["region"] = pd.cut(
    longitude,
    bins=[-np.inf, q1, q2, np.inf],
    labels=["West", "Central", "East"]
)

print("\nGeographic regions:")
print(df["region"].value_counts())

# ==========================================
# 4. Spatial train/test split
# ==========================================
#
# Train on West + Central
# Test on East
#
# This means the model has to predict an
# unseen geographic region.
# ==========================================

train_mask = df["region"].isin(["West", "Central"])
test_mask = df["region"] == "East"

X_train = X[train_mask]
X_test = X[test_mask]

y_train = y[train_mask]
y_test = y[test_mask]

print("\nSpatial split:")
print("Training samples:", len(X_train))
print("Testing samples :", len(X_test))

print("\nTraining labels:")
print(y_train.value_counts())

print("\nTesting labels:")
print(y_test.value_counts())

# ==========================================
# 5. Handle missing values
# ==========================================

imputer = SimpleImputer(strategy="median")

X_train = pd.DataFrame(
    imputer.fit_transform(X_train),
    columns=features
)

X_test = pd.DataFrame(
    imputer.transform(X_test),
    columns=features
)

# ==========================================
# 6. Train XGBoost
# ==========================================

print("\nTraining spatial XGBoost model...")

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

model.fit(X_train, y_train)

# ==========================================
# 7. Predictions
# ==========================================

y_pred = model.predict(X_test)

# ==========================================
# 8. Metrics
# ==========================================

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n===================================")
print("       SPATIAL VALIDATION")
print("===================================")

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

# ==========================================
# 9. Feature importance
# ==========================================

importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print("\n===== FEATURE IMPORTANCE =====")

print(importance)

print("\nSpatial validation completed.")