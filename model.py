import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import pickle

# Load dataset
df = pd.read_csv('balanced_data2.csv', encoding='ISO-8859-1')

df = df.drop(columns=["player_name"], errors="ignore")
df['injury_risk_score'] = df['n_injuries'] * 2 + df['n_severe_injuries'] * 3

X = df.drop(columns=["currently_injured"])
y = df["currently_injured"]

# Apply SMOTE
try:
    smote = SMOTE(random_state=42, sampling_strategy='auto')
    X, y = smote.fit_resample(X, y)
except ValueError:
    pass

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save feature names for consistency with app.py
pickle.dump(list(X_train.columns), open('X_train_columns.pkl', 'wb'))

# Calculate class weights
class_weights = dict(zip(np.unique(y_train), 1 / np.bincount(y_train) * len(y_train)))

# Define XGBoost model
xgb = XGBClassifier(
    n_estimators=400,
    learning_rate=0.03,
    max_depth=5,
    min_child_weight=3,
    gamma=0.3,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=class_weights[1] * 2,
    random_state=42
)

# Hyperparameter search
tuned_params = {
    'n_estimators': [300, 400, 500],
    'max_depth': [4, 5, 6],
    'learning_rate': [0.02, 0.03, 0.04],
    'min_child_weight': [2, 3, 4],
    'gamma': [0.2, 0.3, 0.4],
    'scale_pos_weight': [class_weights[1] * 1.5, class_weights[1] * 2, class_weights[1] * 2.5]
}

search = RandomizedSearchCV(xgb, param_distributions=tuned_params, n_iter=10, scoring='f1', cv=5, random_state=42)
search.fit(X_train_scaled, y_train)

# Train best model
best_xgb = search.best_estimator_
best_xgb.fit(X_train_scaled, y_train)

# Evaluate model
y_pred = best_xgb.predict(X_test_scaled)
y_prob = best_xgb.predict_proba(X_test_scaled)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("Model Performance:")
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

# Save model and scaler
pickle.dump(best_xgb, open('model.pkl', 'wb'))
pickle.dump(scaler, open('scaler.pkl', 'wb'))
# Add injury risk score to test data
for player in test_players:
    player['injury_risk_score'] = player['n_injuries'] * 2 + player['n_severe_injuries'] * 3

# Convert to DataFrame
test_df = pd.DataFrame(test_players)

# Ensure same features as training data
missing_cols = set(X_train.columns) - set(test_df.columns)
for col in missing_cols:
    test_df[col] = 0

# Reorder columns
test_df = test_df[X_train.columns]

# Scale test data
test_df_scaled = scaler.transform(test_df)

# Get probability scores
proba = best_xgb.predict_proba(test_df_scaled)[:, 1]

# Much more aggressive threshold for high-risk players
final_threshold = 0.3  # Fixed lower threshold

# Custom prediction logic
predictions = []
for i, prob in enumerate(proba):
    player = test_players[i]
    
    # Automatic injury prediction if high injury count or risk factors
    if (player['n_injuries'] >= 3 or 
        player['n_severe_injuries'] >= 1 or 
        player['injury_risk_score'] >= 6 or 
        prob >= final_threshold):
        predictions.append(1)
    else:
        predictions.append(0)

# Print detailed results
print("\nPredictions for test players:")
for i, (pred, prob) in enumerate(zip(predictions, proba)):
    player = test_players[i]
    risk_score = player['injury_risk_score']
    
    risk_level = "High" if (risk_score >= 6 or prob > 0.4) else "Medium" if (risk_score >= 3 or prob > 0.2) else "Low"
    status = "🔴 Likely Injured" if pred == 1 else "🟢 Likely Not Injured"
    
    print(f"\nPlayer {i+1}:")
    print(f"Status: {status}")
    print(f"Probability: {prob:.2f}")
    print(f"Risk Level: {risk_level}")
    print(f"Injury Risk Score: {risk_score}")
    
    # Always print risk factors
    print("Risk Factors:")
    if player['n_injuries'] > 0:
        print(f"  - Previous injuries: {player['n_injuries']} (High Risk)" if player['n_injuries'] >= 3 
              else f"  - Previous injuries: {player['n_injuries']}")
    if player['n_severe_injuries'] > 0:
        print(f"  - Severe injuries: {player['n_severe_injuries']}")
    if player['games'] < 10:
        print("  - Limited game time")
    if player['age'] > 30:
        print("  - Age factor")