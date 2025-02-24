import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
from imblearn.over_sampling import RandomOverSampler

def train_and_save_model():
    # Load dataset
    df = pd.read_csv('balanced_data2.csv', encoding='ISO-8859-1')
    df = df.drop(columns=["player_name"], errors="ignore")

    # Enhanced injury risk scoring with workload management
    df['injury_risk_score'] = (
        df['n_injuries'] * 1.5 + 
        df['n_severe_injuries'] * 2.5 +
        (df['minutes_90s'] > 30).astype(int) * 1.0 +  # Match workload
        (df['minutes'] > 3000).astype(int) * 1.0 +    # Season workload
        (df['age'] > 30).astype(int) * 1.0 +          # Age factor
        (df['games'] < 5).astype(int) * 0.5 +         # Match fitness
        (df['shots'] > 40).astype(int) * 0.5          # Physical exertion
    )

    # Add fitness indicators
    df['match_fitness'] = df['minutes'] / df['games'].clip(lower=1)
    df['workload_intensity'] = df['minutes_90s'] / df['games'].clip(lower=1)

    # Define X and y
    X = df.drop(columns=["currently_injured"])
    y = df["currently_injured"]

    # Calculate class distributions
    n_majority = sum(y == 0)
    n_minority = sum(y == 1)

    # Print class distribution for debugging
    print(f"Original distribution - Majority: {n_majority}, Minority: {n_minority}")

    # Calculate target number for minority class (increase by 50%)
    target_minority = int(n_minority * 2)  # Double the minority class
    
    # Configure sampling strategy
    sampling_strategy = {
        1: min(target_minority, n_majority)  # Don't exceed majority class size
    }

    # Simple random oversampling with explicit numbers
    ros = RandomOverSampler(
        random_state=42,
        sampling_strategy=sampling_strategy
    )
    X, y = ros.fit_resample(X, y)

    # Print new distribution for verification
    print(f"After resampling - Class 0: {sum(y == 0)}, Class 1: {sum(y == 1)}")

    # Train-test split with better stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Enhanced XGBoost parameters
    xgb = XGBClassifier(
        n_estimators=500,
        learning_rate=0.01,
        max_depth=4,
        min_child_weight=2,
        gamma=0.2,
        subsample=0.9,
        colsample_bytree=0.9,
        scale_pos_weight=1.2,
        random_state=42
    )

    # Train model
    xgb.fit(X_train_scaled, y_train)

    # Save model, scaler and feature names
    joblib.dump(xgb, 'model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(list(X.columns), 'feature_names.pkl')
    
    return xgb, scaler, list(X.columns)

# Only train if this file is run directly
if __name__ == '__main__':
    train_and_save_model()
