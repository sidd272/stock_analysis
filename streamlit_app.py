import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.title('NIFTY Index High/Low Time Analysis')

# List available CSV files in the current directory

csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

selected_file = st.selectbox('Select NIFTY Index CSV file:', csv_files, index=csv_files.index('NIFTY 50_minute.csv') if 'NIFTY 50_minute.csv' in csv_files else 0)
bucket_size = st.slider('Select bucket size (minutes):', min_value=5, max_value=120, value=15, step=5)

if selected_file:
    df = pd.read_csv(selected_file)
    # st.write('Columns in file:', list(df.columns))
    # Find possible datetime columns
    datetime_candidates = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    if not datetime_candidates:
        st.error('No datetime-like column found in the selected file.')
        # st.write('First few rows:', df.head())
    else:
        # st.write('Sample values from datetime column:', df[datetime_col].head())
        # st.write('Sample date/time columns:', df[['date','time']].head())
        # Group by date and find high/low times
        high_times = []
        low_times = []
        for date, group in df.groupby('date'):
            if 'high' not in group.columns or 'low' not in group.columns or 'time' not in group.columns:
                st.error('CSV must contain "high", "low", and "time" columns.')
                # st.write('Columns found:', list(group.columns))
                st.stop()
            idx_high = group['high'].idxmax()
            idx_low = group['low'].idxmin()
            high_times.append(group.loc[idx_high, 'time'])
            low_times.append(group.loc[idx_low, 'time'])
        # Convert times to minutes since midnight
        def time_to_minutes(tstr):
            h, m, *rest = map(int, tstr.split(':'))
            return h * 60 + m
        high_minutes = [time_to_minutes(t) for t in high_times]
        low_minutes = [time_to_minutes(t) for t in low_times]
        # Discard datimes after 16:00 (960 minutes)
        filtered_high = [(t, m) for t, m in zip(high_times, high_minutes) if m < 960]
        filtered_low = [(t, m) for t, m in zip(low_times, low_minutes) if m < 960]
        high_times, high_minutes = zip(*filtered_high) if filtered_high else ([],[])
        low_times, low_minutes = zip(*filtered_low) if filtered_low else ([],[])
        # Filter dates for which both high and low are present (before 16:00)
        filtered_dates = []
        filtered_high_times = []
        filtered_low_times = []
        for date, h, l in zip(sorted(df['date'].unique()), high_times, low_times):
            if h and l:
                filtered_dates.append(date)
                filtered_high_times.append(h)
                filtered_low_times.append(l)
        # Bucketize
        def bucketize(minutes):
            return (minutes // bucket_size) * bucket_size
        high_buckets = [bucketize(m) for m in high_minutes]
        low_buckets = [bucketize(m) for m in low_minutes]
        # Prepare for plotting
        all_buckets = sorted(set(high_buckets + low_buckets))
        high_counts = [high_buckets.count(b) for b in all_buckets]
        low_counts = [low_buckets.count(b) for b in all_buckets]
        # Plot
        fig, ax = plt.subplots(figsize=(10, 5))
        width = bucket_size * 0.4
        ax.bar([b - width/2 for b in all_buckets], high_counts, width=width, label='Highs', color='orange')
        ax.bar([b + width/2 for b in all_buckets], low_counts, width=width, label='Lows', color='blue')
        ax.set_xticks(all_buckets)
        ax.set_xticklabels([f'{b//60:02d}:{b%60:02d}' for b in all_buckets], rotation=45)
        ax.set_xlabel('Time Bucket')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of Daily High/Low Times')
        ax.legend()
        st.pyplot(fig)
        # List
        st.subheader('List of High/Low Times by Date')
        result_df = pd.DataFrame({'Date': filtered_dates, 'High Time': filtered_high_times, 'Low Time': filtered_low_times})
        st.dataframe(result_df)
