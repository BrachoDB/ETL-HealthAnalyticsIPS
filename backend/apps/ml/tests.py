import tempfile
from datetime import timedelta
from pathlib import Path

import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.ml.models import MLModelMetrics
from apps.ml.services import (
    FEATURE_NAMES_FILE,
    LABEL_ENCODER_FILE,
    MODEL_FILE,
    get_feature_names_path,
    get_label_encoder_path,
    get_model_path,
    hash_file,
)


class FakeModel:
    feature_importances_ = [0.3, 0.2, 0.15, 0.1, 0.08, 0.07, 0.04, 0.03, 0.01, 0.01, 0.005, 0.005]

    def predict(self, data):
        return [1]

    def predict_proba(self, data):
        return [[0.25, 0.75]]


class MLPredictionValidationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='medico', password='password123', role='MEDICO')
        self.client.force_authenticate(user=self.user)
        self.model_dir = tempfile.TemporaryDirectory()
        self.original_media_root = None
        self._patch_model_paths()

    def tearDown(self):
        self.model_dir.cleanup()

    def _patch_model_paths(self):
        import apps.ml.services as services
        from django.conf import settings

        self.original_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.model_dir.name
        services.MODEL_DIR = Path(settings.MEDIA_ROOT) / 'models'

    def _install_model(self, model_hash=None):
        model_path = get_model_path()
        label_encoder_path = get_label_encoder_path()
        feature_names_path = get_feature_names_path()
        model_path.parent.mkdir(parents=True, exist_ok=True)
        label_encoder = LabelEncoder()
        label_encoder.classes_ = np.array(['Bajo', 'Crítico'])
        joblib.dump(FakeModel(), model_path)
        joblib.dump(label_encoder, label_encoder_path)
        joblib.dump(['edad', 'imc', 'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca', 'glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura', 'antecedentes_familiares', 'fumador', 'consumo_alcohol'], feature_names_path)

        MLModelMetrics.objects.create(
            model_name='random_forest',
            model_version='test_v1',
            model_path=str(model_path),
            model_hash=model_hash or hash_file(model_path),
            label_encoder_hash=hash_file(label_encoder_path),
            feature_names_hash=hash_file(feature_names_path),
            accuracy=1.0,
            precision=1.0,
            recall=1.0,
            f1_score=1.0,
            confusion_matrix=[[0, 0], [0, 1]],
            feature_names=['edad', 'imc', 'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca', 'glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura', 'antecedentes_familiares', 'fumador', 'consumo_alcohol'],
            trained_at=timezone.now() - timedelta(minutes=1),
        )

    def _valid_payload(self):
        return {
            'edad': 30,
            'imc': 24.22,
            'presion_sistolica': 120,
            'presion_diastolica': 80,
            'frecuencia_cardiaca': 70,
            'glucosa': 90.0,
            'colesterol': 180.0,
            'saturacion_oxigeno': 98.0,
            'temperatura': 36.5,
            'antecedentes_familiares': False,
            'fumador': False,
            'consumo_alcohol': False,
        }

    def test_invalid_prediction_payload_returns_400(self):
        response = self.client.post('/api/ml/predict/', self._valid_payload() | {'edad': 130}, format='json')

        self.assertEqual(response.status_code, 400)

    def test_invalid_batch_payload_returns_400(self):
        response = self.client.post('/api/ml/predict/batch/', [self._valid_payload() | {'edad': 130}], format='json')

        self.assertEqual(response.status_code, 400)

    def test_valid_prediction_with_trained_model(self):
        self._install_model()

        response = self.client.post('/api/ml/predict/', self._valid_payload(), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['riesgo_predicho'], 'Crítico')
        self.assertIn('explicacion', response.data)
        self.assertGreaterEqual(len(response.data['explicacion']), 1)
        self.assertIn('advertencia_clinica', response.data)

    def test_altered_model_returns_503(self):
        self._install_model(model_hash='hash-alterado')

        response = self.client.post('/api/ml/predict/', self._valid_payload(), format='json')

        self.assertEqual(response.status_code, 503)
