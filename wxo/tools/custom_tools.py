# custom_tools.py
import os, io, base64
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
import traceback
import requests
import warnings
warnings.filterwarnings("ignore") # you dont want these in tool outputs


from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission


# External file server endpoint
IMAGE_SERVER_URL = "https://w07jz4f3-8000.uks1.devtunnels.ms"
FILE_SERVER_UPLOAD = f"{IMAGE_SERVER_URL}/image"

# Datasets
DATASET_SPECS = {
    "TechSales": {
        "file": "tech_sales_data.csv",
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
    #spec = _get_dataset_spec(dataset)
    #url = spec.get("url")
    

    
    #TESTDATA = u"""\
    #transaction_id,date,year,month,quarter,category,product_name,unit_price,quantity,total_amount,customer_segment,sales_channel,region,sales_rep
    #TXN-3132FC7F,2023-04-21,2023,4,Q2,Smartphones,Samsung Galaxy S24,847.98,1,847.98,Consumer,Online,Latin America,
    #TXN-3CECF7D2,2022-11-09,2022,11,Q4,Smartphones,iPhone 15 Pro,1042.73,4,4170.92,Consumer,Retail Store,Latin America
    #"""
    
    BANKING_TEST_DATA = u"""id,date,amount,vendor,category,		
    1,14/09/2025,2.88,LIDL,FOOD,
    2,13/09/2025,17.08,LIDL,FOOD,
    3,11/09/2025,36.00,STATION,TRAVEL,
    4,10/09/2025,237.00,COUNCIL,UTILITY,
    5,09/09/2025,400.00,MARMOT,VACATION,
    6,08/09/2025,12.00,AMAZON,SHOPPING,
    7,07/09/2025,15.00,AMAZON,SHOPPING,
    8,06/09/2025,5.00,TESCO,FOOD,
    9,05/09/2025,3.50,TESCO,FOOD,
    10,04/09/2025,7.00,TESCO,FOOD,
    11,03/09/2025,50.00,TRAIN,TRAVEL,
    12,02/09/2025,30.00,TRAIN,TRAVEL,
    13,01/09/2025,20.00,TRAIN,TRAVEL,
    14,31/08/2025,100.00,RENT,UTILITY,
    15,30/08/2025,60.00,GAS,UTILITY,
    """
    
    MAXIMO_TEST_DATA = u"""id,sla,report_date,target_fix_date,actual_fix_date,work_description,
    WO8734,S1,14/09/2025,20/09/2025,18/09/2025,Replace air filter,
    WO4534,S2,13/09/2025,15/09/2025,16/09/2025,Fix leaking pipe,
    WO3431,S3,11/09/2025,12/09/2025,11/09/2025,Repair broken window,
    WO6454,S5,10/09/2025,14/09/2025,13/09/2025,Service HVAC system,
    WO7342,S1,09/09/2025,10/09/2025,10/09/2025,Replace light bulbs,
    WO6353,S4,08/09/2025,09/09/2025,10/09/2025,Fix door lock,
    WO6341,S5,07/09/2025,08/09/2025,07/09/2025,Repair roof leak,
    WO6322,S1,06/09/2025,07/09/2025,06/09/2025,Service elevator,
    WO8453,S4,05/09/2025,06/09/2025,05/09/2025,Replace carpet,
    WO6327,S5,04/09/2025,05/09/2025,04/09/2025,Fix plumbing issue,
    WO3463,S1,03/09/2025,04/09/2025,03/09/2025,Repair parking lot,
    WO3432,S3,02/09/2025,03/09/2025,02/09/2025,Service fire alarm system,
    WO4567,S3,01/09/2025,02/09/2025,01/09/2025,Replace ceiling tiles,
    WO4533,S1,31/08/2025,01/09/2025,31/08/2025,Fix exterior lighting,
    WO6233,S2,30/08/2025,31/08/2025,02/09/2025,Repair sidewalk,
    WO6234,S4,29/08/2025,30/08/2025,29/08/2025,Service sprinkler system,
    WO6235,S5,28/08/2025,29/08/2025,28/08/2025,Replace HVAC filters,
    """
        
    try:
        df = pd.read_csv(io.StringIO(MAXIMO_TEST_DATA), index_col=-1, sep=r",\s*", engine='python')
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

    return df


def _df_to_markdown_with_csv(df: pd.DataFrame, limit: int = 20):
    """Return a markdown preview and optional CSV attachment (base64) to upload to the file server."""
    if isinstance(df, pd.Series):
        df = df.to_frame(name="value")

    preview = df.head(limit)
    text = preview.to_markdown(index=False, tablefmt="github")


    attachments = []
    if len(df) > limit:
        text += f"\n\n_Results truncated to {limit} rows (total: {len(df)}). Full CSV attached._"
        csv_b64 = base64.b64encode(df.to_csv(index=False).encode("utf-8")).decode("utf-8")
        attachments.append({"name": "result.csv", "mimetype": "text/csv", "base64": csv_b64})
    return text, attachments

def _attach_chart_if_any():
    """Capture the current matplotlib figure as PNG (base64) if axes exist."""
    
    #plt.figure(figsize=(100,60))
        
    fig = plt.gcf()

    if fig and fig.get_axes():
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=160)
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        return [{"name": "chart.png", "mimetype": "image/png", "base64": b64}]
    return []
    
    
    
def _upload_bytes_to_file_server(image_bytes) -> str:
    """
    POSTs the file to the server and returns the public URL.
    Expects the  server to respond with JSON {"url": "..."}.
    """

    payload = {
    "data": image_bytes  }
    
    headers = {
    'Content-Type': 'application/json',
     }

    response = requests.request("POST", FILE_SERVER_UPLOAD, headers=headers, json=payload)

    print(response.url)
    
    response.raise_for_status()
    jresponse = response.json()
    return jresponse.get("url", "") # e.g. "https://w07jz4f3-8000.uks1.devtunnels.ms/assets/chart.jpg"

def _attachments_to_markdown(att_list: list):
    """
    For each attachment, upload to the Flask server and return Markdown links:
      - PNG -> ![name](URL)
      - CSV/other -> [Download name](URL)
    """
    blocks = []
    for a in att_list or []:
        b64 = a.get("base64")
        if not b64:
            continue
        name = a.get("name") or "file"
        mime = a.get("mimetype") or "application/octet-stream"

        try:
            url = _upload_bytes_to_file_server(b64)
        except Exception as e:
            # fall back: show an error line for visibility
            blocks.append(f"_Upload failed for {name}: {e}_")
            continue

        if mime == "image/png":
            blocks.append(f"![{name}]({url})")
        elif mime == "text/csv":
            blocks.append(f"[Download {name}]({url})")
        else:
            blocks.append(f"[Download {name}]({url})")
    return "\n\n".join(blocks)

def _compose_return(text: str, attachments: list):
    """Append Markdown links/images using the Flask-hosted URLs"""
    md = _attachments_to_markdown(attachments)
    if md:
        return f"{text}\n\n{md}"
    return text


# TOOLS
@tool(
    name="excel_schema_preview_52",
    description=(
        "Inspect the selected dataset (TechSales). "
        "Returns dataset key, logical table name, description, row/column counts, full column list with dtypes, and head(5). "
        "Use this first to understand schema before writing code."
    ),
    permission=ToolPermission.READ_ONLY
)
def excel_schema_preview(dataset: str = "TechSales") -> str:
    """
    Args:
      dataset: 'TechSales'.
    
    Returns:
      Plain text summary: dataset, table name, description, row/column counts, column list + dtypes, and head(5).
    """
    spec = _get_dataset_spec(dataset)
    df = _load_df(dataset)
    lines = []
    lines.append(f"Dataset: {dataset}")
    lines.append(f"Table: {spec.get('table_name')}")
    if spec.get("description"):
        lines.append(f"Description: {spec.get('description')}")
    lines.append(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
    lines.append("Columns: " + ", ".join(df.columns))
    dtypes = "\n".join([f"- {c}: {str(t)}" for c, t in df.dtypes.items()])
    lines.append("\nDtypes:\n" + dtypes)
    lines.append("\nHead(5):\n" + df.head(5).to_string(index=False))
    return "\n".join(lines)


def _normalize_code(s: str) -> str:
    if s is None:
        return ""
    # If it looks like it's all on one line with \n sequences, decode them.
    try:
        # This turns "\\n" into actual newlines, "\\t" into tabs, etc.
        return s.encode("utf-8").decode("unicode_escape")
    except Exception:
        return s.replace("\\n", "\n").replace("\\t", "\t")


@tool(
    name="python_sandbox_52",
    description=(
        "Uses pre-loaded DataFrames and execute Python (pandas/matplotlib) code. "
        "CRITICAL: DONT USE double quote, always single quotes and provide complete code."
        "CRITICAL: Do not generate code to read read csv file.  Always use 'df_DATASETNAME' format, e.g., 'df_TechSales'. "
        "CRITICAL: Set final output to variable named 'result'. Python code MUST end with result = ..."
        "DataFrames/Series return Markdown previews (<=20 rows); charts/full CSVs are attached as markdown links. "
        "Doesn't write files to disk, captures the current matplotlib figure and auto-upload."
        "On error, returns full exception type, message, traceback, and the executed code."
    ),
    permission=ToolPermission.READ_ONLY
)
def python_sandbox(python: str, dataset: str = "TechSales") -> str:
    """
    Args:
      python: Python code to execute. Set final output set to a variable named 'result'.
              Always use 'df_DATASETNAME' format, e.g., 'df_TechSales'.
              
      dataset: (e.g., 'TechSales'.

    Returns:
      - Returns final output from the variable named 'result'.
      - If it is a DataFrame/Series: markdown preview (<=20 rows) + CSV markdown link if large.
      - If a chart was drawn: attaches chart.png in markdown.
      - On error: returns full error type, message, traceback, and the exact code that ran.
    """
    
    ds = "TechSales"
    
    # Load datasets
    dataframe =  _load_df(ds)
 
    # Create global namespace, it will be passed into exec as variables
    g = {"pd": pd, "np": np, "plt": plt}
    l = {}
    
    g[f"df_{ds}"] = dataframe
    
    plt.show = lambda: None # Override plt.show to do nothing, we dont want it to print Axes(...) - confuses the llm when tool returns it
    try:
        python = _normalize_code(python)
        exec(python, g, l)

    except FileNotFoundError as fnf_err:
        # If FileNotFoundError, retry without loading the file (dataframes are already pre-loaded)
        # sometimes llm writes code that tries to load the file from disk
        # Just return a message indicating the DataFrame is already pre-loaded
        return (
            "FileNotFoundError: The requested file was not found, but the DataFrame is already pre-loaded and available as 'df_<DATASET>'.\n"
            "Do not attempt to load the file from disk or URL. Use the pre-loaded DataFrame variable.\n"
            f"Error details: {fnf_err}\n"
            "python code used:\n```python\n" + (python or "") + "\n```"
        )

    except Exception as e:
        tb = traceback.format_exc()
        
        g_vars = list(g.keys())

        return (
            "Python execution error:\n"
            f"{type(e).__name__}: {e}\n"
            f"Traceback:\n{tb}\n\n"
            "python code used:\n```python\n" + (python or "") + "\n```"
            f"Vars loaded: {g_vars}"
            "Retry tool call with fixed code"
        )

    result = l.get("result", g.get("result", None))
    attachments = _attach_chart_if_any()

    if result is None and attachments == []: # if there's no table attached, and no plot attached, throw error
        return (
            _compose_return("Error: No `result` produced. Assign your final object to `result`.", attachments)
            + "\n\npython code used:\n```python\n" + (python or "") + "\n```"
        )

    if isinstance(result, (pd.DataFrame, pd.Series)):
        text, more = _df_to_markdown_with_csv(result, limit=20)
        attachments.extend(more)
        return _compose_return(text, attachments)

    return _compose_return(str(result), attachments)
