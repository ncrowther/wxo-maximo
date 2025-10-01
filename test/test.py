import matplotlib.pyplot as plt
import pandas as pd
import io

COS_BASE_URL = "https://asksow-data.s3.us-east.cloud-object-storage.appdomain.cloud"
CSV_DATA = f"{COS_BASE_URL}/workorders2.csv"

# Dataset
DATASET_SPECS = {
    "TechSales": {
        "url": CSV_DATA,
        "description": "Tech sales dataset",
        "table_name": "tech_sales_data",
    }
}

# Helpers functions
def _get_dataset_spec(dataset: str) -> dict:
    ds = (dataset or "").strip()
    if ds not in DATASET_SPECS:
        raise ValueError(
            f"Unknown dataset '{dataset}'. Expected one of: {', '.join(DATASET_SPECS.keys())}."
        )
    return DATASET_SPECS[ds]

def _load_df(dataset: str = "TechSales") -> pd.DataFrame:
    """Load the selected dataset as a DataFrame.

    Args:
        dataset: One of 'TechSales'.
    """
    spec = _get_dataset_spec(dataset)
    url = spec.get("url")
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
    except Exception:
        # Optional, add fallback?: eg try local Excel workbook
        raise

    # Parse likely datetime columns if present
    for col in df.columns:
        if "date" in col.lower() or "start" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="ignore")
            except Exception:
                pass

    # Save the DataFrame as CSV to working directory for agent convenience - so doesnt have to download it everytime
    # You need to change agent permissions or it will error
    # csv_filename = f"{dataset}.csv"
    # df.to_csv(csv_filename, index=False)

    return df

####### Main code starts here ######
df_TechSales = _load_df()

####### INSERT GENERATED CODE BELOW #######
#  >>>>>>>>

import matplotlib.pyplot as plt

# Group by 'status' and count the number of work orders
status_counts = df_TechSales['status'].value_counts()

# Create a pie chart
plt.figure(figsize=(8, 8))
plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Work Orders by Status')
plt.tight_layout()

# Save the result
result = plt.gcf()


# <<<<<<<<

######## KEEP THE LINE BELOW TO DISPLAY THE CHART ########
print(result)
plt.show()