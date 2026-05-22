from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import shap
import os

app = FastAPI(
    title="API Prédiction ROI & Mix Média",
    description="API REST pour estimer la performance et le ROI des campagnes publicitaires, avec explicabilité SHAP.",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models at startup
print("Chargement des modèles...")
MODELS_DIR = "models"
try:
    scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    encoder = joblib.load(os.path.join(MODELS_DIR, "encoder.pkl"))
    clf_perf = joblib.load(os.path.join(MODELS_DIR, "classifier_perf.pkl"))
    reg_roi = joblib.load(os.path.join(MODELS_DIR, "regressor_roi.pkl"))
    shap_bg = joblib.load(os.path.join(MODELS_DIR, "shap_background.pkl"))
    
    # Recreate SHAP explainer
    print("Création de l'Explainer SHAP...")
    explainer = shap.KernelExplainer(reg_roi.predict, shap_bg)
except Exception as e:
    print(f"Erreur lors du chargement des modèles : {e}")

features_num = ['TV', 'Radio', 'Social Media']

# Modèle de données pour valider automatiquement le JSON en entrée
class BudgetScenario(BaseModel):
    TV: float = Field(..., description="Budget alloué à la TV (ex: 50.0)")
    Radio: float = Field(..., description="Budget alloué à la Radio (ex: 20.0)")
    Social_Media: float = Field(..., alias="Social Media", description="Budget alloué aux Réseaux Sociaux (ex: 5.0)")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "TV": 50.0,
                "Radio": 20.0,
                "Social Media": 5.0
            }
        }

def _preprocess_input(scenario: BudgetScenario):
    """ Helper function to scale numerical inputs. """
    raw_df = pd.DataFrame([[scenario.TV, scenario.Radio, scenario.Social_Media]], columns=features_num)
    scaled_array = scaler.transform(raw_df)
    scaled_df = pd.DataFrame(scaled_array, columns=features_num)
    return scaled_df

@app.post("/predict/performance", summary="Prédire la Catégorie de Performance")
def predict_performance(scenario: BudgetScenario):
    """
    Détermine si le scénario budgétaire donnera une 'Haute Performance' ou 'Basse Performance'.
    """
    try:
        X_scaled = _preprocess_input(scenario)
        
        pred_encoded = clf_perf.predict(X_scaled)[0]
        pred_label = encoder.inverse_transform([pred_encoded])[0]
        
        proba = clf_perf.predict_proba(X_scaled)[0]
        confidence = round(float(max(proba)) * 100, 2)
        
        return {
            "status": "success",
            "Performance_Prediction": str(pred_label),
            "Confidence_Percentage": confidence
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict/roi", summary="Estimer le ROI (Valeur exacte)")
def predict_roi(scenario: BudgetScenario):
    """
    Estime le Retour sur Investissement (ROI) exact en % via le Réseau de Neurones Profond.
    """
    try:
        X_scaled = _preprocess_input(scenario)
        
        # Predict performance implicitly required by the regression model
        pred_encoded = clf_perf.predict(X_scaled)[0]
        pred_label = encoder.inverse_transform([pred_encoded])[0]
        
        X_reg = X_scaled.copy()
        X_reg['Performance_encoded'] = pred_encoded
        
        # Predict ROI
        roi_pred = reg_roi.predict(X_reg)[0]
        
        return {
            "status": "success",
            "Performance_Implicit_Prediction": str(pred_label),
            "ROI_Prediction_Percentage": round(float(roi_pred), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict/shap_impact", summary="Analyser l'Impact des Canaux (SHAP)")
def predict_shap(scenario: BudgetScenario):
    """
    Décompose la prédiction du ROI pour comprendre mathématiquement l'impact de chaque canal publicitaire.
    Idéal pour les scénarios combinatoires.
    """
    try:
        X_scaled = _preprocess_input(scenario)
        
        pred_encoded = clf_perf.predict(X_scaled)[0]
        
        X_reg = X_scaled.copy()
        X_reg['Performance_encoded'] = pred_encoded
        
        shap_values = explainer.shap_values(X_reg)
        base_value = float(explainer.expected_value)
        
        features = features_num + ['Performance']
        impact = {feat: round(float(val), 4) for feat, val in zip(features, shap_values[0])}
        
        predicted_roi = base_value + sum(shap_values[0])
        
        return {
            "status": "success",
            "Base_ROI_Average": round(base_value, 2),
            "Predicted_ROI": round(float(predicted_roi), 2),
            "SHAP_Impact_Breakdown": impact
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    print("Démarrage du serveur FastAPI via Uvicorn sur le port 8000...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
