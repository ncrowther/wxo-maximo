import matplotlib.pyplot as plt
import pandas as pd
import io

DATA_SET = "data.csv"
COS_BASE_URL = "https://asksow-data.s3.us-east.cloud-object-storage.appdomain.cloud"
CSV_DATA = f"{COS_BASE_URL}/{DATA_SET}"

#https://imageserv.1fc3gg6j1yh7.eu-gb.codeengine.appdomain.cloud/transactions_202510021134.csv

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

import pandas as pd

# Filter pending work orders
pending_work_orders = df_TechSales[df_TechSales['status'] == 'PENDING']

# Calculate breaches
pending_work_orders['Breach Days'] = (pd.to_datetime('today') - pending_work_orders['target_fix_date']).dt.days

# Filter breached work orders
breached_work_orders = pending_work_orders[pending_work_orders['Breach Days'] > 0]

# Set the result
result = breached_work_orders[['work_order', 'Breach Days']]

# <<<<<<<<

######## KEEP THE LINE BELOW TO DISPLAY THE CHART ########
print(result)
plt.show()