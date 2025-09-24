import matplotlib.pyplot as plt
import pandas as pd
import io

def _load_df() -> pd.DataFrame:
    """Load the selected dataset as a DataFrame.

    """
    
    MAXIMO_TEST_DATA = u"""work_order,sla,status,report_date,target_fix_date,actual_fix_date,permanent_repair_deadline,work_description,
    WO8734,S1,COMPLETED,14/09/2025,20/09/2025,28/09/2025,,Replace air filter,
    WO4534,S2,PENDING,13/09/2025,15/09/2025,,,Fix leaking pipe. Temporary fix applied,
    WO3431,S3,COMPLETED,11/09/2025,12/09/2025,11/09/2025,,Repair broken window,
    WO6454,S5,COMPLETED,10/09/2025,14/09/2025,13/09/2025,,Service HVAC system,
    WO7342,S1,COMPLETED,09/09/2025,10/09/2025,10/09/2025,,Replace light bulbs,
    WO6353,S4,COMPLETED,08/09/2025,09/09/2025,10/09/2025,,Fix door lock,
    WO6341,S5,COMPLETED,07/09/2025,08/09/2025,07/09/2025,,Repair roof leak,
    WO6322,S1,PENDING,06/09/2025,07/09/2025,,,Service elevator,
    WO8453,S4,COMPLETED,05/09/2025,06/09/2025,05/09/2025,,Replace carpet,
    WO6327,S5,COMPLETED,04/09/2025,05/09/2025,04/09/2025,,Fix plumbing issue,
    WO3463,S1,PENDING,03/09/2025,04/09/2025,,,Repair parking lot,
    WO3432,S3,COMPLETED,02/09/2025,03/09/2025,02/09/2025,,Service fire alarm system,
    WO4567,S3,PENDING,01/09/2025,02/09/2025,,,Replace ceiling tiles. Temporary fix applied,
    WO4533,S1,COMPLETED,31/08/2025,01/09/2025,31/08/2025,,Fix exterior lighting,
    WO6233,S2,COMPLETED,30/08/2025,31/08/2025,02/09/2025,,Repair sidewalk,
    WO6234,S4,PENDING,29/08/2025,30/08/2025,,,Service sprinkler system,
    WO6235,S5,COMPLETED,28/08/2025,29/08/2025,28/08/2025,,Replace HVAC filters,
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