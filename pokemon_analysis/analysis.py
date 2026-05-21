import pandas as pd

# Load the Pokemon dataset
df = pd.read_csv("pokemon_gen1to7_dataset.csv")

# Create a simple column description table
column_summary = pd.DataFrame({
    "Column Name": df.columns,
    "Data Type": df.dtypes.values,
    "Value Type": [
        "Numeric" if pd.api.types.is_numeric_dtype(df[col]) else "Text / Category"
        for col in df.columns
    ],
    "Unique Values": [df[col].nunique() for col in df.columns],
    "Missing Values": [df[col].isna().sum() for col in df.columns],
    "Missing %": [(df[col].isna().mean() * 100).round(2) for col in df.columns], # type: ignore
    "Sample Values": [
        ", ".join(df[col].dropna().astype(str).unique()[:3])
        for col in df.columns
    ]
})

# Show result
print(column_summary)

# Optional: export to CSV
column_summary.to_csv("pokemon_column_summary.csv", index=False)