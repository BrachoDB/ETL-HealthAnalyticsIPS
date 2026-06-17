import hashlib
from pathlib import Path

import joblib
from django.conf import settings

from apps.ml.models import MLModelMetrics


MODEL_DIR = Path(settings.MEDIA_ROOT) / 'models'
MODEL_FILE = 'random_forest_model.joblib'
LABEL_ENCODER_FILE = 'label_encoder.joblib'
FEATURE_NAMES_FILE = 'feature_names.joblib'
MODEL_VERSION = 'random_forest_v1'


class ModelIntegrityError(RuntimeError):
    pass


def get_model_dir():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR


def get_model_path():
    return get_model_dir() / MODEL_FILE


def get_label_encoder_path():
    return get_model_dir() / LABEL_ENCODER_FILE


def get_feature_names_path():
    return get_model_dir() / FEATURE_NAMES_FILE


def hash_file(path):
    path = Path(path)
    if not path.exists():
        return None
    sha256 = hashlib.sha256()
    with path.open('rb') as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_current_model_hashes():
    return {
        'model_hash': hash_file(get_model_path()),
        'label_encoder_hash': hash_file(get_label_encoder_path()),
        'feature_names_hash': hash_file(get_feature_names_path()),
    }


def get_latest_model_metadata():
    metric = MLModelMetrics.objects.order_by('-trained_at').first()
    if not metric or not metric.model_hash:
        return None

    current_hashes = get_current_model_hashes()
    expected_hashes = {
        'model_hash': metric.model_hash,
        'label_encoder_hash': metric.label_encoder_hash,
        'feature_names_hash': metric.feature_names_hash,
    }

    if current_hashes != expected_hashes:
        raise ModelIntegrityError('Los artefactos del modelo no coinciden con el hash registrado.')

    return metric


def load_model_bundle_metadata():
    return get_latest_model_metadata()


def load_model_bundle():
    metadata = load_model_bundle_metadata()
    path = get_model_path()
    label_encoder_path = get_label_encoder_path()
    feature_names_path = get_feature_names_path()
    if not path.exists():
        raise FileNotFoundError(f'El modelo no existe: {path}')
    model = joblib.load(path)
    label_encoder = joblib.load(label_encoder_path)
    feature_names = joblib.load(feature_names_path)
    return model, label_encoder, feature_names, metadata


def build_explanation(model, feature_names):
    importances = getattr(model, 'feature_importances_', None)
    if importances is None or not hasattr(model, 'predict_proba'):
        return []

    pairs = sorted(zip(feature_names, importances), key=lambda item: item[1], reverse=True)
    return [
        {'feature': feature, 'importance': round(float(importance), 6)}
        for feature, importance in pairs[:5]
    ]
