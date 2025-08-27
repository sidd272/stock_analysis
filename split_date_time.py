import pandas as pd
import glob

# Get all CSV files in the current directory
csv_files = glob.glob('*.csv')

for file in csv_files:
    df = pd.read_csv(file)
    if 'date' in df.columns:
        # Split 'date' column into 'date' and 'time'
        split_dt = df['date'].astype(str).str.split(' ', n=1, expand=True)
        df['date'] = split_dt[0]
        if split_dt.shape[1] > 1:
            df['time'] = split_dt[1]
        else:
            df['time'] = ''
        # Save back to the same file, keeping column order
        cols = list(df.columns)
        # Move 'time' right after 'date'
        if 'time' in cols:
            cols.insert(cols.index('date') + 1, cols.pop(cols.index('time')))
        df = df[cols]
        df.to_csv(file, index=False)
        print(f'Processed {file}')
    else:
        print(f'Skipped {file} (no date column)')
