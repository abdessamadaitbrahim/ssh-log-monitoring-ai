import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

data = pd.read_csv('../data/processed/preprocessed_ssh_logs.csv')
features = data[['is_private', 'is_root', 'is_valid', 'ip_failure', 'ip_success', 'no_failure']]
X_train, X_test, y_train, y_test = train_test_split(features, data['anomaly'], test_size=0.2, random_state=42)
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_train)
y_pred = model.predict(X_test)
y_pred = [1 if x == -1 else 0 for x in y_pred]
print(classification_report(y_test, y_pred))
joblib.dump(model, '../data/processed/ssh_ai_model.pkl')
print("Modèle IA entraîné et sauvegardé sous 'data/processed/ssh_ai_model.pkl'")
