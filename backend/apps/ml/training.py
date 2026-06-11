import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from django.conf import settings
from apps.etl.models import Patient

def train_model():
    # 1. Cargar datos desde la BD
    patients = Patient.objects.all().values()
    if not patients:
        print("No hay datos en la BD para entrenar.")
        return
    
    df = pd.DataFrame(list(patients))
    
    # 2. Preprocesamiento
    # Seleccionamos variables predictoras
    features = [
        'edad', 'imc', 'presion_sistolica', 'presion_diastolica', 
        'frecuencia_cardiaca', 'glucosa', 'colesterol', 
        'saturacion_oxigeno', 'temperatura', 'antecedentes_familiares', 
        'fumador', 'consumo_alcohol'
    ]
    
    X = df[features]
    y = df['riesgo_enfermedad']
    
    # Encode target
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Encode categoricals in X (if any were strings, but here they are bool/float)
    # antecedentes_familiares, fumador, consumo_alcohol are already bool/int
    
    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    # 4. Train
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Evaluate
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1': f1_score(y_test, y_pred, average='weighted'),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
    }
    
    print(f"Accuracy: {metrics['accuracy']}")
    
    # 6. Save Model and Encoder
    ml_dir = os.path.join(settings.BASE_DIR, 'apps', 'ml', 'saved_models')
    os.makedirs(ml_dir, exist_ok=True)
    
    joblib.dump(model, os.path.join(ml_dir, 'random_forest_model.pkl'))
    joblib.dump(le, os.path.join(ml_dir, 'label_encoder.pkl'))
    joblib.dump(features, os.path.join(ml_dir, 'feature_names.pkl'))
    
    return metrics

if __name__ == "__main__":
    # This is for testing standalone, but usually called from a command
    pass
