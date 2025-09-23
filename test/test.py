import matplotlib.pyplot as plt
import pandas as pd
import io

def _load_df() -> pd.DataFrame:
    """Load the selected dataset as a DataFrame.

    """
    
    MAXIMO_TEST_DATA = u"""id,report_date,target_fix_date,actual_fix_date,work_description,
    1,14/09/2025,20/09/2025,21/09/2025,Replace air filter,
    2,13/09/2025,15/09/2025,16/09/2025,Fix leaking pipe,
    3,11/09/2025,12/09/2025,12/09/2025,Repair broken window,
    4,10/09/2025,14/09/2025,14/09/2025,Service HVAC system,
    5,09/09/2025,10/09/2025,10/09/2025,Replace light bulbs,
    6,08/09/2025,09/09/2025,10/09/2025,Fix door lock,
    7,07/09/2025,08/09/2025,08/09/2025,Repair roof leak,
    8,06/09/2025,07/09/2025,07/09/2025,Service elevator,
    9,05/09/2025,06/09/2025,06/09/2025,Replace carpet,
    10,04/09/2025,05/09/2025,07/09/2025,Fix plumbing issue,
    11,03/09/2025,04/09/2025,04/09/2025,Repair parking lot,
    12,02/09/2025,03/09/2025,07/09/2025,Service fire alarm system,
    13,01/09/2025,02/09/2025,02/09/2025,Replace ceiling tiles,
    14,31/08/2025,01/09/2025,01/09/2025,Fix exterior lighting,
    15,30/08/2025,31/08/2025,02/09/2025,Repair sidewalk,

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

# Calculate the number of breached and on-time work orders
breached = df_TechSales[df_TechSales['actual_fix_date'] > df_TechSales['target_fix_date']].shape[0]
on_time = df_TechSales[df_TechSales['actual_fix_date'] <= df_TechSales['target_fix_date']].shape[0]

# Create a pie chart
labels = ['Breached', 'On Time']
sizes = [breached, on_time]
colors = ['#ff9999','#66b3ff']
explode = (0.1, 0)

plt.figure(figsize=(8, 8))
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
plt.axis('equal')
plt.title('Work Orders: Breached vs On Time')

# Save the result
result = plt.gcf()

# <<<<<<<<

######## KEEP THE LINE BELOW TO DISPLAY THE CHART ########
plt.show()