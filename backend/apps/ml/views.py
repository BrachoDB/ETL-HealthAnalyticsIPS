import pandas as pd
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ml.services import load_model_bundle


class PredictionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if isinstance(request.data, list):
            return Response({'error': 'Use /api/ml/predict/batch/ para predicciones masivas.'}, status=status.HTTP_400_BAD_REQUEST)
        return self._predict([request.data], single=True)

    def _predict(self, records, single=False):
        try:
            if not records:
                return Response({'error': 'No se enviaron registros para predecir.'}, status=status.HTTP_400_BAD_REQUEST)

            model, label_encoder, feature_names = load_model_bundle()
            df_input = pd.DataFrame(records)
            missing_features = [feature for feature in feature_names if feature not in df_input.columns]
            if missing_features:
                return Response({'error': f'Faltan campos: {", ".join(missing_features)}'}, status=status.HTTP_400_BAD_REQUEST)

            df_input = df_input[feature_names]
            prediction_encoded = model.predict(df_input)
            predictions = label_encoder.inverse_transform(prediction_encoded)

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
                    })
            else:
                results = [{'riesgo_predicho': prediction, 'probabilidades': {}} for prediction in predictions]

            if single:
                return Response(results[0])

            return Response({'total': len(results), 'resultados': results})

        except FileNotFoundError:
            return Response({'error': 'El modelo no ha sido entrenado.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BatchPredictionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not isinstance(request.data, list):
            return Response({'error': 'El cuerpo de la solicitud debe ser una lista de registros.'}, status=status.HTTP_400_BAD_REQUEST)
        return PredictionAPIView()._predict(request.data, single=False)
