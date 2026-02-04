import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

def train_f1_model():
    print("🧠 Training the F1 Strength Model...")
    
    # 1. Load Data
    drivers = pd.read_csv('drivers.csv')
    constructors = pd.read_csv('constructors.csv')
    circuits = pd.read_csv('circuits.csv')
    races = pd.read_csv('races.csv')
    results = pd.read_csv('results.csv')

    # 2. Pre-process & Define Target (Strength Index)
    results.replace('\\N', np.nan, inplace=True)
    results['positionOrder'] = pd.to_numeric(results['positionOrder'], errors='coerce')
    
    # Score Formula: 100 for 1st, reduced by 5 for every position down.
    # We add 5 bonus points if they had the fastest lap (rank 1)
    results['strength_score'] = 100 - (results['positionOrder'] - 1) * 5
    results.loc[results['rank'] == '1', 'strength_score'] += 5
    results['strength_score'] = results['strength_score'].clip(0, 100)

    # 3. Merge Datasets
    df = results.merge(races[['raceId', 'circuitId']], on='raceId')
    df = df.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
    df = df.merge(constructors[['constructorId', 'name']], on='constructorId', suffixes=('', '_team'))

    # 4. Feature Engineering: Historical Power Ratings
    # Calculate lifetime average scores for drivers, teams, and circuits
    driver_stats = df.groupby('driverId')['strength_score'].mean().reset_index().rename(columns={'strength_score': 'driver_power'})
    team_stats = df.groupby('constructorId')['strength_score'].mean().reset_index().rename(columns={'strength_score': 'team_power'})
    circuit_stats = df.groupby('circuitId')['strength_score'].mean().reset_index().rename(columns={'strength_score': 'circuit_difficulty'})

    # Merge ratings back to the training set
    df = df.merge(driver_stats, on='driverId')
    df = df.merge(team_stats, on='constructorId')
    df = df.merge(circuit_stats, on='circuitId')

    # 5. Model Training (Linear Regression)
    X = df[['driver_power', 'team_power', 'circuit_difficulty']]
    y = df['strength_score']
    model = LinearRegression()
    model.fit(X, y)

    # 6. Save Model and Lookup Files for Streamlit
    joblib.dump(model, 'f1_strength_model.pkl')
    
    # Save lookups with names for the UI to use
    driver_stats = driver_stats.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
    driver_stats['driver_name'] = driver_stats['forename'] + " " + driver_stats['surname']
    driver_stats[['driver_name', 'driver_power']].to_csv('driver_lookup.csv', index=False)

    team_stats = team_stats.merge(constructors[['constructorId', 'name']], on='constructorId')
    team_stats[['name', 'team_power']].to_csv('team_lookup.csv', index=False)

    circuit_stats = circuit_stats.merge(circuits[['circuitId', 'name']], on='circuitId')
    circuit_stats[['name', 'circuit_difficulty']].to_csv('circuit_lookup.csv', index=False)

    print("✅ ML Model and Lookups saved successfully.")

# Inference Helper for Streamlit
def get_prediction(driver_name, team_name, circuit_name):
    model = joblib.load('f1_strength_model.pkl')
    d_lookup = pd.read_csv('driver_lookup.csv').set_index('driver_name')
    t_lookup = pd.read_csv('team_lookup.csv').set_index('name')
    c_lookup = pd.read_csv('circuit_lookup.csv').set_index('name')
    
    try:
        d_p = d_lookup.loc[driver_name, 'driver_power']
        t_p = t_lookup.loc[team_name, 'team_power']
        c_p = c_lookup.loc[circuit_name, 'circuit_difficulty']
        
        score = model.predict([[d_p, t_p, c_p]])[0]
        score = min(max(score, 0), 100)
        
        tier = "Elite" if score > 85 else "Strong" if score > 70 else "Midfield" if score > 45 else "Backmarker"
        return round(score, 1), tier
    except KeyError:
        return None, "Data Not Found"

if __name__ == "__main__":
    train_f1_model()