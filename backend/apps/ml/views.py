import numpy as np
import pandas as pd
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.permissions import IsAdminOrMedico
from apps.ml.models import PredictionAudit
from apps.ml.serializers import BatchPredictionSerializer, PredictionInputSerializer
from apps.ml.services import MODEL_VERSION, ModelIntegrityError, build_explanation, get_model_path, load_model_bundle, load_model_bundle_metadata


class PredictionAPIView(APIView):
    permission_classes = [IsAdminOrMedico]
    serializer_class = PredictionInputSerializer

    def post(self, request):
        if isinstance(request.data, list):
            return Response({'error': 'Use /api/ml/predict/batch/ para predicciones masivas.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            # Depuración: imprime el detalle exacto de validación
            print("[DEBUG] /api/ml/predict/ serializer.errors:", serializer.errors)
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Validación clínica robusta antes de invocar el modelo (aditiva)
        from apps.ml.utils import validar_datos_clinicos
        try:
            validar_datos_clinicos(serializer.validated_data)
        except ValueError as exc:
            # Auditoría del intento fallido con trazabilidad (requisito)
            PredictionAudit.objects.create(
                user=request.user,
                model_name='random_forest',
                model_version=MODEL_VERSION,
                model_path=str(get_model_path()),
                model_hash=None,
                input_data=[serializer.validated_data],
                prediction={
                    'error': str(exc),
                    'reason': 'Intento de predicción con datos fuera de rango clínico',
                },
            )
            # Nota: el modelo no se ejecuta.
            return Response(
                {'error': str(exc)},
                status=422,
            )

        return self._predict([serializer.validated_data], single=True, user=request.user, source='api')


    def _predict(self, records, single=False, user=None, source='api'):
        try:
            if not records:
                return Response({'error': 'No se enviaron registros para predecir.'}, status=status.HTTP_400_BAD_REQUEST)

            model, label_encoder, feature_names, metadata = load_model_bundle()
            df_input = pd.DataFrame(records)
            missing_features = [feature for feature in feature_names if feature not in df_input.columns]
            if missing_features:
                return Response({'error': f'Faltan campos: {", ".join(missing_features)}'}, status=status.HTTP_400_BAD_REQUEST)

            df_input = df_input[feature_names]
            prediction_encoded = np.asarray(model.predict(df_input))
            predictions = label_encoder.inverse_transform(prediction_encoded)

            explanation = build_explanation(model, feature_names)
            results = []
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(df_input)
                for index, prediction in enumerate(predictions):
                    prob_dict = {
                        label_encoder.inverse_transform([class_index])[0]: float(probabilities[index][class_index])
                        for class_index in range(len(label_encoder.classes_))
                    }
                    results.append({
                        'riesgo_predicho': prediction,
                        'probabilidades': prob_dict,
                        'explicacion': explanation,
                    })
            else:
                results = [{'riesgo_predicho': prediction, 'probabilidades': {}, 'explicacion': explanation} for prediction in predictions]

            audit_payload = {
                'input_data': records,
                'prediction': results,
                'source': source,
            }
            PredictionAudit.objects.create(
                user=user,
                model_name='random_forest',
                model_version=getattr(metadata, 'model_version', MODEL_VERSION) if metadata else MODEL_VERSION,
                model_path=str(get_model_path()),
                model_hash=getattr(metadata, 'model_hash', None) if metadata else None,
                input_data=records,
                prediction=audit_payload,
            )

            metadata_response = self._metadata_response(metadata)
            if single:
                response = results[0].copy()
                response.update(metadata_response)
                return Response(response)

            response = {'total': len(results), 'resultados': results}
            response.update(metadata_response)
            return Response(response)

        except FileNotFoundError:
            return Response({'error': 'El modelo no ha sido entrenado.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except ModelIntegrityError:
            return Response({'error': 'El modelo no pasó la validación de integridad.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _metadata_response(self, metadata):
        if not metadata:
            return {
            'model_version': MODEL_VERSION,
            'model_hash': None,
            'trained_at': None,
            'advertencia_clinica': 'Esta predicción es una ayuda analítica y no reemplaza el juicio clínico profesional.',
            }

        return {
            'model_version': metadata.model_version,
            'model_hash': metadata.model_hash,
            'trained_at': metadata.trained_at.strftime('%Y-%m-%d %H:%M:%S'),
            'advertencia_clinica': 'Esta predicción es una ayuda analítica y no reemplaza el juicio clínico profesional.',
        }


class BatchPredictionAPIView(APIView):
    permission_classes = [IsAdminOrMedico]
    serializer_class = BatchPredictionSerializer

    def post(self, request):
        if not isinstance(request.data, list):
            return Response({'error': 'El cuerpo de la solicitud debe ser una lista de registros.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data={'records': request.data})
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return PredictionAPIView()._predict(serializer.validated_data['records'], single=False, user=request.user, source='api-batch')
