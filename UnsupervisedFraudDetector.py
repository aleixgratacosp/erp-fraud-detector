import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

class UnsupervisedFraudDetector:
    def __init__(self, csv_file):
        columns_to_use = ["transaction_id","user_id", "customer_id", "product_category", "total_amount", 
                               "discount_percent","timestamp_order","shipping_date", "invoice_date", 
                               "order_status", "is_fraud"]
        self.original_transactions = pd.read_csv(csv_file, sep=';', usecols=columns_to_use)

    def _prepare_data_iforest(self):
        """ Feature engineering phase for iforest algorithm. Only fit for: Discount Manipulation, Premature Invoicing, Channel Stuffing. """

        df = self.original_transactions.copy()
        original_index = df.index

        user_avg_disc = df.groupby('user_id')['discount_percent'].transform('mean')
        df['discount_relative_impact'] = df['discount_percent'] / (user_avg_disc + 0.01)

        df['total_amount_log'] = np.log1p(df['total_amount'])
        

        cust_avg_amt = df.groupby('customer_id')['total_amount'].transform('mean')
        df['amount_vs_history'] = df['total_amount'] / (cust_avg_amt + 1)


        df['shipping_date'] = pd.to_datetime(df['shipping_date'], errors='coerce')
        df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')
        df['days_for_shipping'] = (df['shipping_date'] - df['invoice_date']).dt.days.fillna(0)

        features = [
            "total_amount_log", 
            "discount_percent", 
            "discount_relative_impact", 
            "amount_vs_history",
            "days_for_shipping"
        ]
        
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df[features])
    
        return pd.DataFrame(scaled_features, columns=features, index=original_index)
    
    def _prepare_data(self):
        """ Feature engineering phase for LOF algorithm. Fit for all types of fraud """
        df = self.original_transactions.copy()
        original_index = df.index

        df['timestamp_order'] = pd.to_datetime(df['timestamp_order'])
        df['shipping_date'] = pd.to_datetime(df['shipping_date'], errors='coerce')
        df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')

        df['order_hour'] = df['timestamp_order'].dt.hour
        df['is_december'] = (df['timestamp_order'].dt.month == 12).astype(int)
        df['days_for_shipping'] = (df['shipping_date'] - df['invoice_date']).dt.days.fillna(0) 

        # Used for splitting detection: To see how much time difference we have for any set of user and customer
        df = df.sort_values(by=['user_id', 'customer_id', 'timestamp_order'])
        df['seconds_since_last'] = df.groupby(['user_id', 'customer_id'])['timestamp_order'].diff().dt.total_seconds()
        
        mean_seconds = df['seconds_since_last'].mean()
        df['seconds_since_last'] = df['seconds_since_last'].fillna(mean_seconds)
        
        df = df.sort_index()

        df['user_avg_discount'] = df.groupby('user_id')['discount_percent'].transform('mean')
        df['customer_avg_amount'] = df.groupby('customer_id')['total_amount'].transform('mean')

        scaler = StandardScaler()
        
        features = [
            "total_amount", "discount_percent", "order_hour", "is_december",
            "days_for_shipping", "seconds_since_last", "user_avg_discount", "customer_avg_amount"
        ]
        
        df_features = df[features]
        scaled_features = scaler.fit_transform(df_features)
        
        return pd.DataFrame(scaled_features, columns=features, index=original_index)
    
    def execute_detection(self, algorithm='iforest', model_contamination=0.023, num_estimators=200, num_max_samples=1000):

        if algorithm == 'iforest':
            data_to_detect = self._prepare_data_iforest()
            #n = 200 and m = 1000 have been chosen due to its superior performance
            model = IsolationForest(contamination=model_contamination, n_estimators=num_estimators, max_samples=num_max_samples)
            predictions = model.fit_predict(data_to_detect)
            anomaly_scores = -model.decision_function(data_to_detect)
            
        elif algorithm == 'lof':
            data_to_detect = self._prepare_data()
            model = LocalOutlierFactor(n_neighbors=20, contamination=model_contamination)
            predictions = model.fit_predict(data_to_detect)
            anomaly_scores = -model.negative_outlier_factor_
        
        self.original_transactions['final_risk_score'] = (pd.Series(anomaly_scores).rank(pct=True) * 100).round(2)
        self.original_transactions['ai_is_fraud'] = [1 if p == -1 else 0 for p in predictions]
        return self.original_transactions
    

    def execute_ensemble(self, threshold_score=99.0):

        data_lof = self._prepare_data()
        model_lof = LocalOutlierFactor(contamination=0.0048)
        model_lof.fit_predict(data_lof)
        
        # LOF returns anomalies ranked from more to least anomalous. Lower the negative number, higher the risk.
        lof_risk = pd.Series(-model_lof.negative_outlier_factor_).rank(pct=True) * 100

        data_if = self._prepare_data_iforest()
        model_if = IsolationForest(n_estimators=200, max_samples=1000, contamination=0.0093)
        model_if.fit(data_if)
        if_risk = pd.Series(-model_if.decision_function(data_if)).rank(pct=True) * 100

        # We take the maximum of each score
        self.original_transactions['final_risk_score'] = np.maximum(lof_risk, if_risk).round(2)
        
        self.original_transactions['ai_is_fraud'] = (self.original_transactions['final_risk_score'] >= threshold_score).astype(int)
        
        return self.original_transactions
            
    #For debugging
    def evaluate(self):
        print("EVALUATE FUNCTION ====== ")
        true_fraud = (self.original_transactions['is_fraud'] > 0).astype(int)
        fraud_prediction = self.original_transactions['ai_is_fraud']
    
        print(classification_report(true_fraud, fraud_prediction))
    
        v_confusion_matrix = confusion_matrix(true_fraud, fraud_prediction)
        print("Confusion Matrix:")
        print(f"True Positives: {v_confusion_matrix[1,1]}")
        print(f"False Positives: {v_confusion_matrix[0,1]}")
        print(f"False Negatives: {v_confusion_matrix[1,0]}")
