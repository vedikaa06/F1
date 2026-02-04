import pandas as pd

def perform_advanced_engineering():
    print("🛠️ Performing Advanced Feature Engineering...")
    df = pd.read_csv('f1_master_dataset.csv')

    # 1. Driver Career Stats (The "Strength" of the human)
    # We calculate cumulative win rate up to that point in time
    df = df.sort_values(['driverId', 'date'])
    df['driver_win_rate'] = df.groupby('driverId')['is_win'].transform(lambda x: x.expanding().mean())
    df['driver_podium_rate'] = df.groupby('driverId')['is_podium'].transform(lambda x: x.expanding().mean())

    # 2. Team Career Stats (The "Strength" of the car)
    df = df.sort_values(['constructorId', 'date'])
    df['team_win_rate'] = df.groupby('constructorId')['is_win'].transform(lambda x: x.expanding().mean())
    df['team_reliability'] = df.groupby('constructorId')['positionOrder'].transform(lambda x: x.expanding().mean())

    # 3. Circuit Complexity
    # We define complexity by how much the 'grid' (start) differs from 'positionOrder' (finish)
    df['position_gain'] = df['grid'] - df['positionOrder']
    circuit_stats = df.groupby('circuitId')['position_gain'].std().reset_index().rename(columns={'position_gain': 'circuit_variability'})
    df = df.merge(circuit_stats, on='circuitId', how='left')

    # 4. Final Score Target (The 0-100 Score)
    # This is a calculated label for training: 100 for a win, decreasing as rank drops.
    # Formula: Max(0, 100 - (Position * 5)) + (Points * 2)
    df['performance_score'] = (100 - (df['positionOrder'] * 4)) + (df['points'] * 0.5)
    df['performance_score'] = df['performance_score'].clip(0, 100)

    # Save the file for the ML Model
    df.to_csv('f1_features_ready.csv', index=False)
    print("✅ Success! 'f1_features_ready.csv' is ready for the ML model.")

if __name__ == "__main__":
    perform_advanced_engineering()