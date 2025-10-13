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


# Data set
DATA_SET = "data.csv"
#COS_BASE_URL = "https://asksow-data.s3.us-east.cloud-object-storage.appdomain.cloud"
COS_BASE_URL = "https://wxo-maximo-data.s3.us.cloud-object-storage.appdomain.cloud"
CSV_DATA = f"{COS_BASE_URL}/{DATA_SET}"

# External file server endpoint
IMAGE_SERVER_URL = "https://imageserv.1fc3gg6j1yh7.eu-gb.codeengine.appdomain.cloud"
IMAGE_UPLOAD = f"{IMAGE_SERVER_URL}/image"
CSV_UPLOAD = f"{IMAGE_SERVER_URL}/csv"

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

    response = requests.request("POST", IMAGE_UPLOAD, headers=headers, json=payload)
    
    response.raise_for_status()
    jresponse = response.json()
    return jresponse.get("url", "") # e.g. "https://w07jz4f3-8000.uks1.devtunnels.ms/assets/chart.jpg"

def _upload_csv_to_server(csv_data) -> str:
    """
    POSTs the file to the server and returns the public URL.
    Expects the  server to respond with JSON {"url": "..."}.
    """

    payload = {
    "data": csv_data  }
    
    headers = {
    'Content-Type': 'application/json',
     }

    response = requests.request("POST", CSV_UPLOAD, headers=headers, json=payload)
    
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
        #data = base64.b64decode(b64)

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
    name="excel_schema_preview_57",
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
    name="python_sandbox_57",
    description=(
        "Uses pre-loaded DataFrames and execute Python (pandas/matplotlib) code. "
        "CRITICAL: DONT USE double quote, always single quotes and provide complete code."
        "Always use 'df_DATASETNAME' format, e.g., 'df_TechSales'. "
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
    dataset_list = [ds.strip() for ds in dataset.split(",")]
    
    # Validate datasets exists in pre-defined list
    for ds in dataset_list:
        if ds not in DATASET_SPECS:
            return f"Error: Unknown dataset '{ds}'. Available datasets: {', '.join(DATASET_SPECS.keys())}"
    
    # Load datasets
    dataframes = {}
    for ds in dataset_list:
        try:
            dataframes[ds] = _load_df(ds)
        except Exception as e:
            return f"Error loading dataset '{ds}': {e}"
    
    # Create global namespace, it will be passed into exec as variables
    g = {"pd": pd, "np": np, "plt": plt}
    l = {}
    

    # Multiple datasets: use df_DATASETNAME format
    for ds, df_for_ds in dataframes.items():
        g[f"df_{ds}"] = df_for_ds
    
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
        # local_files = "\n".join(os.listdir("."))
        return (
            "Python execution error:\n"
            f"{type(e).__name__}: {e}\n"
            f"Traceback:\n{tb}\n\n"
            "python code used:\n```python\n" + (python or "") + "\n```"
            f"Vars loaded: {g_vars}"
            # f"Local files: {local_files}"
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


@tool(permission=ToolPermission.READ_ONLY)
def upload_csv_file(document: bytes) -> str:
    """
    Uploads a document and returns the location as a URL
    :returns: the document URL
    """
    
    csv = document.decode("ascii")
    
    url = _upload_csv_to_server(csv)
        
    return url