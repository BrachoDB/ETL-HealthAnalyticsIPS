from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
import joblib
import os
import pandas as pd
from django.conf import settings

class PredictionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Load model and encoders
            ml_dir = os.path.join(settings.BASE_DIR, 'apps', 'ml', 'saved_models')
            model = joblib.load(os.path.join(ml_dir, 'random_forest_model.pkl'))
            le = joblib.load(os.path.join(ml_dir, 'label_encoder.pkl'))
            feature_names = joblib.load(os.path.join(ml_dir, 'feature_names.pkl'))
            
            # Extract data from request
            data = request.data
            
            # Ensure all required features are present
            input_data = []
            for feat in feature_names:
                if feat not in data:
                    return Response({'error': f'Falta el campo: {feat}'}, status=status.HTTP_400_BAD_REQUEST)
                input_data.append(data[feat])
            
            # Predict
            df_input = pd.DataFrame([input_data], columns=feature_names)
            prediction_encoded = model.predict(df_input)[0]
            prediction_label = le.inverse_transform([prediction_encoded])[0]
            
            # Probabilities (optional)
            probabilities = model.predict_proba(df_input)[0]
            prob_dict = {le.inverse_transform([i])[0]: probabilities[i] for i in range(len(le.classes_))}
            
            return Response({
                'riesgo_predicho': prediction_label,
                'probabilidades': prob_dict
            })
            
        except FileNotFoundError:
            return Response({'error': 'El modelo no ha sido entrenado.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
