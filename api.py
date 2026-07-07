from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
from generator import LogGenerator
from fraud_injector import FraudInjector
from UnsupervisedFraudDetector import UnsupervisedFraudDetector
import config

app = Flask(__name__)
CORS(app)

@app.route('/api/phase1/generate', methods=['POST'])
def generate_base_logs():

    try:
        data = request.json
        if data is not None:
            if 'amount' in data:
                try:
                    numberofLogs = int(data['amount'])
                except (ValueError, TypeError):
                    numberofLogs = 100000 
            else:
                numberofLogs = 100000 
        else:
            numberofLogs = 100000
            
        gen = LogGenerator()
        logs = gen.generate_clean_logs(numberofLogs)
        logs.to_csv("dataset_base.csv", index=False, sep=";") 
        
        return jsonify({
            "status": "success",
            "message": "Phase 1 Complete:" + str(numberofLogs) + " legal ERP transactions generated successfully.",
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/phase2/inject', methods=['POST'])
def inject_fraud():
    try:
        if request.json:
            data = request.json
        else:
            data = {}
        
        num_ghost = int(data.get('num_ghost', 392))
        num_chstuff = int(data.get('num_chstuff', 392))
        num_discounts = int(data.get('num_discounts', 392))
        num_unusualh = int(data.get('num_unusualh', 392))
        num_splitting = int(data.get('num_splitting', 130))
        num_prematureinv = int(data.get('num_prematureinv', 392))

        injector = FraudInjector.from_csv("dataset_base.csv")
        
        injectedlogs = injector.inject_all_frauds(
            num_ghost=num_ghost, 
            num_chstuff=num_chstuff, 
            num_discounts=num_discounts, 
            num_unusualh=num_unusualh, 
            num_splitting=num_splitting, 
            num_prematureinv=num_prematureinv
        )
        
        #We will use fraudlogs for the ground-truth later
        fraudlogs = injectedlogs[injectedlogs['is_fraud'] > 0]

        injectedlogs.to_csv("dataset_injected.csv", index=False, sep=";") 
        fraudlogs.to_csv("fraudtestcase.csv", index=False, sep=";")     
        
        total_injected = len(fraudlogs)
        
        return jsonify({
            "status": "success",
            "message": "Phase 2 Complete: Injected " + str(total_injected) + " fraudulent anomalies successfully.",
            "total_real_frauds": total_injected
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/phase3/detect', methods=['POST'])
def detect_fraud():
    try:
        # /localhost:5000/api/phase3/detect?algo=iforest. if none selected, all are picked
        algo = request.args.get('algo', 'all')

        if request.json:
            data = request.json
        else:
            data = {}

        user_contamination = data.get('contamination')

        detector = UnsupervisedFraudDetector("./dataset_injected.csv")
        
        if algo == 'iforest':

            if user_contamination is not None:
                contamination = float(user_contamination)
            else:
                contamination = config.IFOREST_DEFAULT_CONTAMINATION
                
            result_df = detector.execute_detection(algorithm='iforest', model_contamination=contamination)
            result_df.to_csv("dataset_output_iforest.csv", index=False, sep=";")
            
        elif algo == 'lof':
            if user_contamination is not None:
                contamination = float(user_contamination)
            else:
                contamination = config.LOF_DEFAULT_CONTAMINATION
                
            result_df = detector.execute_detection(algorithm='lof', model_contamination=contamination)
            result_df.to_csv("dataset_output_lof.csv", index=False, sep=";")
            
        elif algo == 'ensemble':
            if user_contamination is not None and user_contamination > 1:
                threshold = float(user_contamination)
            else:
                threshold = config.ENSEMBLE_DEFAULT_THRESHOLD
                
            result_df = detector.execute_ensemble(threshold_score=threshold)
            result_df.to_csv("dataset_output_ensemble.csv", index=False, sep=";")
            
        else:
            return jsonify({"status": "error", "message": algo}), 400

        result_df = result_df.fillna("")

        #We first transform dates (datetime) to strings to avoid issues
        for col in ['timestamp_order', 'shipping_date', 'invoice_date']:
            if col in result_df.columns:
                result_df[col] = result_df[col].astype(str)

        records = result_df.to_dict(orient='records')
        return jsonify({"status": "success", "algorithm": algo, "data": records}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    


@app.route('/api/phase5/metrics', methods=['GET'])
def get_performance_metrics():
    try:
        results = {}
        algorithms = ['iforest', 'lof', 'ensemble']

        for algo in algorithms:
            file_path = f"dataset_output_{algo}.csv"
            
            if not os.path.exists(file_path):
                results[algo] = {
                    "accuracy": 0, "precision": 0, "recall": 0,
                    "tp": 0, "fp": 0, "fn": 0, "tn": 0,
                    "caught_breakdown": {}, "not_executed": True
                }
            else:
                df = pd.read_csv(file_path, sep=";")
                #Ground-truth
                y_true = (df['is_fraud'] > 0).astype(int)

                #AI prediction
                y_pred = df['ai_is_fraud']

                cm = confusion_matrix(y_true, y_pred)
                
                if cm.shape == (2, 2):
                    tp = int(cm[1, 1])
                    fp = int(cm[0, 1])
                    fn = int(cm[1, 0])
                    tn = int(cm[0, 0])
                else:
                    tp = 0
                    fp = 0
                    fn = 0
                    tn = 0


                detected_df = df[df['ai_is_fraud'] == 1].copy()
                caught_counts = {name: 0 for name in config.FRAUD_TYPE_MAP.values()}
                
                #count types of detected fraud
                if not detected_df.empty:
                    detected_df['fraud_type_name'] = detected_df['is_fraud'].map(config.FRAUD_TYPE_MAP)
                    counts = detected_df['fraud_type_name'].value_counts().to_dict()
                    for name, count in counts.items():
                        caught_counts[name] = int(count)

                results[algo] = {
                    "accuracy": round(accuracy_score(y_true, y_pred) * 100, 2),
                    "precision": round(precision_score(y_true, y_pred, zero_division=0) * 100, 2),
                    "recall": round(recall_score(y_true, y_pred, zero_division=0) * 100, 2),
                    "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                    "caught_breakdown": caught_counts
                }

        return jsonify({"status": "success", "metrics": results}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)