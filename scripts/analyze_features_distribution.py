import pandas as pd
import numpy as np

# ==========================================
# 1. Load dataset
# ==========================================

DATA_PATH = r"data\training_data.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)


# ==========================================
# 2. Features to analyze
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


# ==========================================
# 3. Compare classes
# ==========================================

print("\n==========================================")
print(" LANDSLIDE vs NON-LANDSLIDE DISTRIBUTIONS")
print("==========================================")

rows = []

for feature in features:

    landslide = df[df["label"] == 1][feature].dropna()
    non_landslide = df[df["label"] == 0][feature].dropna()

    rows.append({
        "Feature": feature,

        "Landslide Mean": landslide.mean(),
        "Non-Landslide Mean": non_landslide.mean(),

        "Landslide Median": landslide.median(),
        "Non-Landslide Median": non_landslide.median(),

        "Landslide Std": landslide.std(),
        "Non-Landslide Std": non_landslide.std(),

        "Landslide Min": landslide.min(),
        "Landslide Max": landslide.max(),

        "Non-Landslide Min": non_landslide.min(),
        "Non-Landslide Max": non_landslide.max()
    })


comparison = pd.DataFrame(rows)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.float_format", "{:.4f}".format)

print(comparison.to_string(index=False))


# ==========================================
# 4. Mean difference
# ==========================================

print("\n==========================================")
print(" ABSOLUTE MEAN DIFFERENCE")
print("==========================================")

for feature in features:

    landslide_mean = df[
        df["label"] == 1
    ][feature].mean()

    non_landslide_mean = df[
        df["label"] == 0
    ][feature].mean()

    difference = abs(
        landslide_mean - non_landslide_mean
    )

    print(
        f"{feature:10s}: {difference:.4f}"
    )


# ==========================================
# 5. Correlation with label
# ==========================================

print("\n==========================================")
print(" CORRELATION WITH LANDSLIDE LABEL")
print("==========================================")

correlations = []

for feature in features:

    correlation = df[
        [feature, "label"]
    ].corr().iloc[0, 1]

    correlations.append(
        (feature, correlation)
    )


correlations.sort(
    key=lambda x: abs(x[1]),
    reverse=True
)


for feature, correlation in correlations:

    print(
        f"{feature:10s}: {correlation:+.4f}"
    )


# ==========================================
# 6. Quantile comparison
# ==========================================

print("\n==========================================")
print(" MEDIAN / QUARTILE COMPARISON")
print("==========================================")

for feature in features:

    landslide = df[
        df["label"] == 1
    ][feature].dropna()

    non_landslide = df[
        df["label"] == 0
    ][feature].dropna()

    print(f"\n--- {feature} ---")

    print(
        "Landslide     : "
        f"Q25={landslide.quantile(.25):.4f}, "
        f"Median={landslide.median():.4f}, "
        f"Q75={landslide.quantile(.75):.4f}"
    )

    print(
        "Non-landslide : "
        f"Q25={non_landslide.quantile(.25):.4f}, "
        f"Median={non_landslide.median():.4f}, "
        f"Q75={non_landslide.quantile(.75):.4f}"
    )


print("\nAnalysis complete.")