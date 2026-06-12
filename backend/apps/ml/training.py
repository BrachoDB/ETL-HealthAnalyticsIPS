import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from apps.etl.models import Patient
from apps.ml.models import MLModelMetrics
from apps.ml.services import get_feature_names_path, get_label_encoder_path, get_model_path


FEATURES = [
    'edad',
    'imc',
    'presion_sistolica',
    'presion_diastolica',
    'frecuencia_cardiaca',
    'glucosa',
    'colesterol',
    'saturacion_oxigeno',
    'temperatura',
    'antecedentes_familiares',
    'fumador',
    'consumo_alcohol',
]


def train_model():
    patients = Patient.objects.all().values()
    if patients.count() == 0:
        print('No hay datos en la BD para entrenar.')
        return None

    df = pd.DataFrame(list(patients))
    if len(df) < 10:
        print('Se requieren al menos 10 registros para entrenar el modelo.')
        return None

    X = df[FEATURES]
    y = df['riesgo_enfermedad']
    if y.nunique() < 2:
        print('Se requieren al menos dos clases de riesgo para entrenar el modelo.')
        return None

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
        'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
    }

    model_path = get_model_path()
    label_encoder_path = get_label_encoder_path()
    feature_names_path = get_feature_names_path()

    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.fit(X, y_encoded)
    import joblib

    joblib.dump(model, model_path)
    joblib.dump(le, label_encoder_path)
    joblib.dump(FEATURES, feature_names_path)

    record = MLModelMetrics.objects.create(
        model_name='random_forest',
        model_path=str(model_path),
        accuracy=metrics['accuracy'],
        precision=metrics['precision'],
        recall=metrics['recall'],
        f1_score=metrics['f1'],
        confusion_matrix=metrics['confusion_matrix'],
        feature_names=FEATURES,
    )
    metrics['model_path'] = str(model_path)
    metrics['record_id'] = record.id
    return metrics


if __name__ == '__main__':
    pass
