from pathlib import Path

import joblib
from django.conf import settings


MODEL_DIR = Path(settings.MEDIA_ROOT) / 'models'
MODEL_FILE = 'random_forest_model.joblib'
LABEL_ENCODER_FILE = 'label_encoder.joblib'
FEATURE_NAMES_FILE = 'feature_names.joblib'


def get_model_dir():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR


def get_model_path():
    return get_model_dir() / MODEL_FILE


def get_label_encoder_path():
    return get_model_dir() / LABEL_ENCODER_FILE


def get_feature_names_path():
    return get_model_dir() / FEATURE_NAMES_FILE


def load_model():
    path = get_model_path()
    if not path.exists():
        raise FileNotFoundError(f'El modelo no existe: {path}')
    return joblib.load(path)


def load_label_encoder():
    path = get_label_encoder_path()
    if not path.exists():
        raise FileNotFoundError(f'El codificador de etiquetas no existe: {path}')
    return joblib.load(path)


def load_feature_names():
    path = get_feature_names_path()
    if not path.exists():
        raise FileNotFoundError(f'Los nombres de características no existen: {path}')
    return joblib.load(path)


def load_model_bundle():
    return load_model(), load_label_encoder(), load_feature_names()
