from __future__ import annotations

import os
from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


FEATURES = [
    'imc',
    'edad',
    'glucosa',
    'colesterol',
    'presion_sistolica',
    'frecuencia_cardiaca',
    'fumador',
]
TARGET = 'riesgo_enfermedad'


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


@dataclass
class ModelArtifacts:
    model_path: str


def train_random_forest(df: pd.DataFrame, model_path: str) -> dict:
    df = df.copy()

    # normalizar nombres esperados
    if 'age' in df.columns and 'edad' not in df.columns:
        df = df.rename(columns={'age': 'edad'})

    required = FEATURES + [TARGET]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = df.dropna(subset=FEATURES + [TARGET])
    if df.empty:
        raise ValueError('No data available to train after dropping missing values')

    X = df[FEATURES]
    y = df[TARGET].astype(str)

    X = X.copy()
    if X['fumador'].dtype == bool:
        X['fumador'] = X['fumador'].map({True: 'True', False: 'False'})

    numeric_cols = ['imc', 'edad', 'glucosa', 'colesterol', 'presion_sistolica', 'frecuencia_cardiaca']
    categorical_cols = ['fumador']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numeric_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols),
        ],
        remainder='drop',
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y if len(set(y)) > 1 else None,
    )

    clf = RandomForestClassifier(
        n_estimators=250,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced',
    )

    pipe = Pipeline(steps=[('pre', preprocessor), ('clf', clf)])
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)

    accuracy = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, average='macro', zero_division=0))
    recall = float(recall_score(y_test, y_pred, average='macro', zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average='macro', zero_division=0))
    cm = confusion_matrix(y_test, y_pred, labels=sorted(list(set(y))))

    _ensure_dir(model_path)
    joblib.dump({'pipeline': pipe, 'labels': sorted(list(set(y)))}, model_path)

    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'confusion_matrix': cm.tolist(),
        'confusion_labels': sorted(list(set(y))),
        'n_train': int(len(X_train)),
        'n_test': int(len(X_test)),
        'model_path': model_path,
    }


def load_model(model_path: str):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f'Model not found at {model_path}')
    payload = joblib.load(model_path)
    return payload['pipeline'], payload['labels']


def predict_risk(model_path: str, input_rows: list[dict]) -> list[dict]:
    pipe, labels = load_model(model_path)

    df = pd.DataFrame(input_rows)
    if 'age' in df.columns and 'edad' not in df.columns:
        df = df.rename(columns={'age': 'edad'})

    for col in FEATURES:
        if col not in df.columns:
            df[col] = None

    X = df[FEATURES]
    preds = pipe.predict(X)

    proba = None
    if hasattr(pipe, 'predict_proba'):
        try:
            proba = pipe.predict_proba(X).tolist()
        except Exception:
            proba = None

    out = []
    for i, p in enumerate(preds):
        item = {'riesgo_predicho': str(p)}
        if proba is not None:
            item['probabilidades'] = {
                str(labels[j]): float(proba[i][j]) for j in range(len(labels))
            }
        out.append(item)

    return out

