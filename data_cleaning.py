import pandas as pd
import numpy as np

def clean_all_f1_data():
    print("🚀 Starting Comprehensive Data Cleaning...")

    # 1. Load ALL provided datasets
    files = [
        'drivers', 'constructors', 'circuits', 'races', 'results', 
        'qualifying', 'pit_stops', 'lap_times', 'sprint_results'
    ]
    dfs = {}
    for f in files:
        dfs[f] = pd.read_csv(f'{f}.csv')
        # Handle the F1-specific '\N' null values immediately
        dfs[f].replace('\\N', np.nan, inplace=True)

    # 2. Basic Merging (The Core)
    master_df = dfs['results'].merge(dfs['races'][['raceId', 'year', 'name', 'circuitId', 'date']], on='raceId', how='left')
    master_df = master_df.merge(dfs['drivers'][['driverId', 'driverRef', 'forename', 'surname', 'nationality']], on='driverId', how='left')
    master_df = master_df.merge(dfs['constructors'][['constructorId', 'constructorRef', 'name', 'nationality']], 
                                on='constructorId', how='left', suffixes=('_race', '_constructor'))
    master_df = master_df.merge(dfs['circuits'][['circuitId', 'name', 'location', 'country']], 
                                on='circuitId', how='left', suffixes=('', '_circuit'))

    # 3. Integrate Qualifying Data (Adding Grid Position vs Qualifying Position)
    if 'qualifying' in dfs:
        # We take the best qualifying position for each driver/race
        quali_slim = dfs['qualifying'][['raceId', 'driverId', 'position']].rename(columns={'position': 'quali_pos'})
        master_df = master_df.merge(quali_slim, on=['raceId', 'driverId'], how='left')

    # 4. Integrate Pit Stop Data (Average Pit Time per Race)
    if 'pit_stops' in dfs:
        dfs['pit_stops']['milliseconds'] = pd.to_numeric(dfs['pit_stops']['milliseconds'], errors='coerce')
        pit_avg = dfs['pit_stops'].groupby(['raceId', 'driverId'])['milliseconds'].mean().reset_index()
        pit_avg.rename(columns={'milliseconds': 'avg_pit_time'}, inplace=True)
        master_df = master_df.merge(pit_avg, on=['raceId', 'driverId'], how='left')

    # 5. Final Cleaning & Feature Engineering
    master_df.rename(columns={'name_race': 'race_name', 'name_constructor': 'team_name', 'name': 'circuit_name'}, inplace=True)
    master_df['driver_full_name'] = master_df['forename'] + ' ' + master_df['surname']
    master_df['decade'] = (pd.to_numeric(master_df['year']) // 10) * 10
    
    # Convert points and positions to numeric
    numeric_cols = ['points', 'positionOrder', 'grid', 'year']
    for col in numeric_cols:
        master_df[col] = pd.to_numeric(master_df[col], errors='coerce').fillna(0)

    # Success Metrics
    master_df['is_win'] = (master_df['positionOrder'] == 1).astype(int)
    master_df['is_podium'] = (master_df['positionOrder'] <= 3).astype(int)

    # 6. Save the Comprehensive Master File
    master_df.to_csv('f1_master_dataset.csv', index=False)
    print(f"✅ Success! Master Dataset created with {master_df.shape[0]} rows and {master_df.shape[1]} columns.")
    return master_df

if __name__ == "__main__":
    clean_all_f1_data()