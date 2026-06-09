from __future__ import annotations

import os
from typing import Any

import pandas as pd
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from sklearn.model_selection import train_test_split

from etl.models import ClinicalRecord

from .utils_rf import FEATURES, TARGET, load_model, predict_risk, train_random_forest


MODEL_DIR = os.path.join(os.getcwd(), 'ml_artifacts')
MODEL_PATH = os.path.join(MODEL_DIR, 'random_forest_model.joblib')


class TrainView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        qs = ClinicalRecord.objects.all()
        if not qs.exists():
            return Response({'detail': 'No hay registros clínicos cargados. Ejecuta /api/etl/run/ primero.'}, status=400)

        rows = list(qs.values(
            'imc', 'age', 'glucosa', 'colesterol', 'presion_sistolica', 'frecuencia_cardiaca', 'fumador',
            TARGET,
        ))
        df = pd.DataFrame(rows)

        try:
            metrics = train_random_forest(df, MODEL_PATH)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

        return Response({'model_path': MODEL_PATH, 'metrics': metrics}, status=201)


class PredictView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        input_rows = request.data.get('inputs')
        if not isinstance(input_rows, list) or not input_rows:
            return Response({'detail': 'Provide payload: {"inputs": [ { ...features } ] }'}, status=400)

        try:
            preds = predict_risk(MODEL_PATH, input_rows)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

        return Response({'model_path': MODEL_PATH, 'predictions': preds}, status=200)


class PredictionsView(APIView):
    """API requerida: /api/predicciones/

    Una operación POST que entrena + evalúa + predice.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        qs = ClinicalRecord.objects.all()
        if not qs.exists():
            return Response({'detail': 'No hay registros clínicos cargados. Ejecuta /api/etl/run/ primero.'}, status=400)

        inputs = request.data.get('inputs', [])
        if inputs is None:
            inputs = []

        rows = list(qs.values(
            'imc', 'age', 'glucosa', 'colesterol', 'presion_sistolica', 'frecuencia_cardiaca', 'fumador',
            TARGET,
        ))
        df = pd.DataFrame(rows)

        metrics: dict[str, Any]
        try:
            metrics = train_random_forest(df, MODEL_PATH)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

        predictions = None
        if isinstance(inputs, list) and inputs:
            try:
                predictions = predict_risk(MODEL_PATH, inputs)
            except Exception:
                predictions = None

        resp = {
            'model_path': MODEL_PATH,
            'metrics': {
                'accuracy': metrics.get('accuracy'),
                'precision': metrics.get('precision'),
                'recall': metrics.get('recall'),
                'f1_score': metrics.get('f1_score'),
                'confusion_matrix': metrics.get('confusion_matrix'),
                'confusion_labels': metrics.get('confusion_labels'),
            },
        }
        if predictions is not None:
            resp['predictions'] = predictions

        return Response(resp, status=201)

