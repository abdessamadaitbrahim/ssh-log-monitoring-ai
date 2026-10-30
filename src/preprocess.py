import pandas as pd
import numpy as np

data = pd.read_csv('../data/raw/ssh_logs.csv') 
print(data.head())
data['is_root'] = data['user'].apply(lambda x: 1 if x == 'root' else 0)
data['is_valid'] = data['user'].apply(lambda x: 1 if x in ['admin', 'user', 'root'] else 0)
data['ip_failure'] = data['is_failure']
data['ip_success'] = 1 - data['is_failure']
data['anomaly'] = data['is_failure'].apply(lambda x: 1 if x == 1 else 0)
data.to_csv('../data/processed/preprocessed_ssh_logs.csv', index=False)
print("Dataset prétraité sauvegardé sous 'data/processed/preprocessed_ssh_logs.csv'")
