from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from analytics.models import Paciente
from .models import MLMetric, Prediccion


class PrediccionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        metrics = MLMetric.objects.order_by('-created_at')[:1]
        last_metric = metrics[0] if metrics else None

        preds = Prediccion.objects.order_by('-created_at')[:200]
        pred_data = [
            {
                'paciente_id': pr.paciente_id,
                'riesgo_probabilidad': pr.riesgo_probabilidad,
                'riesgo_clase': pr.riesgo_clase,
            }
            for pr in preds
        ]

        return Response(
            {
                'metric': {
                    'modelo': last_metric.modelo,
                    'accuracy': last_metric.accuracy,
                    'precision': last_metric.precision,
                    'recall': last_metric.recall,
                    'f1_score': last_metric.f1_score,
                    'confusion_matrix': last_metric.confusion_matrix_json,
                }
                if last_metric
                else None,
                'predicciones': pred_data,
            }
        )


class PrediccionTrainView(APIView):
    """Entrena un modelo para predecir riesgo_enfermedad y genera métricas + predicciones."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Opciones por request
        modelo = request.data.get('modelo', 'random_forest')
        test_size = float(request.data.get('test_size', 0.25))
        random_state = int(request.data.get('random_state', 42))

        # Extraer dataset desde BD
        qs = Paciente.objects.all().values(
            'id_paciente',
            'edad',
            'imc',
            'glucosa',
            'colesterol',
            'presion_sistolica',
            'frecuencia_cardiaca',
            'fumador',
            'riesgo_enfermedad',
        )

        rows = list(qs)
        if not rows:
            return Response({'detail': 'No hay pacientes en la BD para entrenar.'}, status=400)

        # Construir X/y con manejo de nulos
        feature_names = [
            'imc',
            'edad',
            'glucosa',
            'colesterol',
            'presion_sistolica',
            'frecuencia_cardiaca',
            'fumador',
        ]
        label_name = 'riesgo_enfermedad'

        X = []
        y = []
        paciente_ids = []

        for r in rows:
            # Solo entrenar con etiqueta válida
            y_val = (r.get(label_name) or '').strip()
            if not y_val:
                continue

            feat = []
            ok = True
            for f in feature_names:
                v = r.get(f)
                if v is None or (isinstance(v, float) and np.isnan(v)):
                    ok = False
                    break
                feat.append(float(v))

            if not ok:
                continue

            X.append(feat)
            y.append(y_val)
            paciente_ids.append(r['id_paciente'])

        if len(X) < 50:
            return Response(
                {
                    'detail': 'Dataset insuficiente luego del filtrado de nulos para entrenar.',
                    'cantidad': len(X),
                },
                status=400,
            )

        X = np.array(X, dtype=float)
        y = np.array(y)

        # Split
        X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
            X, y, paciente_ids, test_size=test_size, random_state=random_state, stratify=y
        )

        # Modelo
        if modelo == 'logistic_regression':
            clf = LogisticRegression(max_iter=2000, multi_class='auto')
        else:
            clf = RandomForestClassifier(
                n_estimators=200,
                random_state=random_state,
                class_weight='balanced',
            )

        # Entrenamiento
        clf.fit(X_train, y_train)

        # Evaluación
        y_pred = clf.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        cm = confusion_matrix(y_test, y_pred, labels=sorted(list(set(y))))
        cm_json = cm.tolist()

        # Predicciones para TODOS los pacientes válidos
        # (usamos proba si existe)
        if hasattr(clf, 'predict_proba'):
            proba = clf.predict_proba(X)
            clases = clf.classes_
            top_idx = np.argmax(proba, axis=1)
            top_proba = proba[np.arange(len(X)), top_idx]
            top_class = [clases[i] for i in top_idx]
        else:
            top_class = clf.predict(X)
            top_proba = [None] * len(top_class)

        # Reemplazar predicciones anteriores
        Prediccion.objects.all().delete()

        pred_objs = []
        for pid, pc, pp in zip(paciente_ids, top_class, top_proba):
            pred_objs.append(
                Prediccion(
                    paciente_id=int(pid),
                    riesgo_probabilidad=float(pp) if pp is not None else None,
                    riesgo_clase=str(pc),
                )
            )
        Prediccion.objects.bulk_create(pred_objs, batch_size=500)

        # Guardar métricas
        MLMetric.objects.all().delete()
        MLMetric.objects.create(
            modelo=modelo,
            accuracy=float(acc),
            precision=float(prec),
            recall=float(rec),
            f1_score=float(f1),
            confusion_matrix_json={'labels': sorted(list(set(y))), 'matrix': cm_json},
        )

        return Response(
            {
                'detail': 'Entrenamiento ML completado.',
                'dataset': {'cantidad': len(X_train) + len(X_test)},
                'metric': {
                    'modelo': modelo,
                    'accuracy': acc,
                    'precision': prec,
                    'recall': rec,
                    'f1_score': f1,
                    'confusion_matrix': {'labels': sorted(list(set(y))), 'matrix': cm_json},
                },
                'predicciones_generadas': len(pred_objs),
            }
        )


