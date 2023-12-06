import sys
import pandas as pd
import os


## ----------------------------------------------------------------
##  file ans save it as xls
## ----------------------------------------------------------------
def save_csv_as_xls(filename): 
    filenamexls = filename[:-3] + "xlsx"
    try:
        data = pd.read_csv(filename).drop_duplicates()
    except:
        print(f"No file {filename} found")
        return
    
    ## reformat data columns to datetime and float format
    data.iloc[:, 2:] = data.iloc[:, 2:].apply(lambda col: 
        col.apply(pd.to_datetime) if 'time' in col.name.lower() else col.astype(float))
    

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    # Also set the default datetime and date formats.
    sep = '/' if 'ix' in os.name else '\\'
    sheetname = filename.split(sep)[-1].split('_')[0]
    print(sheetname)
    with pd.ExcelWriter(
        filenamexls,
        engine='xlsxwriter',
        datetime_format="DD.MM.YYYY HH:MM",
        date_format="dd.mm.yyyy",
    ) as writer:
    
        data.style \
            .format(precision=3)\
            .to_excel(writer, 
                      sheet_name=sheetname, 
                      index=False,
                      float_format="%.2f", 
                      freeze_panes=(1,0)
                      )
    
        # Get the xlsxwriter workbook and worksheet objects in order
        # to set the column widths and make the dates clearer.
        workbook  = writer.book
        worksheet = writer.sheets[sheetname]

        # Set the column widths, to make the dates clearer.
        worksheet.set_column(2, 5, 20)


for year in range(2022, 2024):
    for month in range(1, 13):
        timestamp = f"{year}-{month:02}"
        filename = "..\\..\\data\\OnLineResult\\" + timestamp + "_OnLineResult.csv"
        save_csv_as_xls(filename)
