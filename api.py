from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as pd
import pandas as pd
import shap
import os

app = Flask(__name__)
CORS(app)

# Load models at startup
print("Loading models...")
MODELS_DIR = "models"
scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
encoder = joblib.load(os.path.join(MODELS_DIR, "encoder.pkl"))
clf_perf = joblib.load(os.path.join(MODELS_DIR, "classifier_perf.pkl"))
reg_roi = joblib.load(os.path.join(MODELS_DIR, "regressor_roi.pkl"))
shap_bg = joblib.load(os.path.join(MODELS_DIR, "shap_background.pkl"))

# Recreate SHAP explainer
print("Recreating SHAP Explainer...")
explainer = shap.KernelExplainer(reg_roi.predict, shap_bg)

features_num = ['TV', 'Radio', 'Social Media']

def _preprocess_input(data):
    """ Helper function to scale numerical inputs. """
    try:
        tv = float(data.get('TV', 0))
        radio = float(data.get('Radio', 0))
        social = float(data.get('Social Media', 0))
    except ValueError:
        raise ValueError("Invalid input values. Must be numeric.")
    
    raw_df = pd.DataFrame([[tv, radio, social]], columns=features_num)
    scaled_array = scaler.transform(raw_df)
    scaled_df = pd.DataFrame(scaled_array, columns=features_num)
    return scaled_df

@app.route('/predict/performance', methods=['POST'])
def predict_performance():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400
    
    try:
        X_scaled = _preprocess_input(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    # Predict performance
    pred_encoded = clf_perf.predict(X_scaled)[0]
    pred_label = encoder.inverse_transform([pred_encoded])[0]
    
    # Get probabilities if available
    proba = clf_perf.predict_proba(X_scaled)[0]
    confidence = round(float(max(proba)) * 100, 2)
    
    return jsonify({
        "status": "success",
        "Performance_Prediction": str(pred_label),
        "Confidence_Percentage": confidence
    })

@app.route('/predict/roi', methods=['POST'])
def predict_roi():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400
    
    try:
        X_scaled = _preprocess_input(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    # First, predict performance because regression needs it
    pred_encoded = clf_perf.predict(X_scaled)[0]
    pred_label = encoder.inverse_transform([pred_encoded])[0]
    
    # Append to features
    X_reg = X_scaled.copy()
    X_reg['Performance_encoded'] = pred_encoded
    
    # Predict ROI
    roi_pred = reg_roi.predict(X_reg)[0]
    
    return jsonify({
        "status": "success",
        "Performance_Implicit_Prediction": str(pred_label),
        "ROI_Prediction_Percentage": round(float(roi_pred), 2)
    })

@app.route('/predict/shap_impact', methods=['POST'])
def predict_shap():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400
    
    try:
        X_scaled = _preprocess_input(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    # Predict performance
    pred_encoded = clf_perf.predict(X_scaled)[0]
    
    # Append to features
    X_reg = X_scaled.copy()
    X_reg['Performance_encoded'] = pred_encoded
    
    # Calculate SHAP values
    shap_values = explainer.shap_values(X_reg)
    
    # Prediction base value (the mean of the background dataset)
    base_value = float(explainer.expected_value)
    
    # Format output
    features = features_num + ['Performance']
    impact = {feat: round(float(val), 4) for feat, val in zip(features, shap_values[0])}
    
    # Predicted ROI is exactly base_value + sum(shap_values)
    predicted_roi = base_value + sum(shap_values[0])
    
    return jsonify({
        "status": "success",
        "Base_ROI_Average": round(base_value, 2),
        "Predicted_ROI": round(float(predicted_roi), 2),
        "SHAP_Impact_Breakdown": impact
    })

if __name__ == '__main__':
    print("Starting Flask API on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
