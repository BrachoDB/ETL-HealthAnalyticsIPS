from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import Paciente
from ml.models import Prediccion
from etl.models import ETLRun


class KPIsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = Paciente.objects.count()
        crit = Paciente.objects.filter(riesgo_enfermedad__iexact='Crítico').count()
        # Conteo total por riesgo (útil para barras/torta)
        riesgo_counts = {
            k: Paciente.objects.filter(riesgo_enfermedad__iexact=k).count()
            for k in ['Bajo', 'Medio', 'Alto', 'Crítico']
        }

        kpis = {
            'total_registros': total,
            'pacientes_criticos': crit,
            'predicciones_total': Prediccion.objects.count(),
            'etl_ejecutados': ETLRun.objects.count(),
            'riesgo_prom_col': Paciente.objects.filter(riesgo_enfermedad__in=['Bajo', 'Medio', 'Alto']).count(),
            'riesgo_counts': riesgo_counts,
        }
        return Response(kpis)


class SegmentacionView(APIView):
    """Devuelve datos para segmentación (edad, sexo, riesgo, diagnóstico, IMC)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Paciente.objects.all()

        def top_counts(field, limit=10):
            return list(
                qs.values_list(field, flat=True)
                .exclude(**{f"{field}__isnull": True})
                .exclude(**{f"{field}__exact": ''})
            )

        # Segmentación por sexo y riesgo (top por conteo)
        sexo = list(
            qs.values('sexo')
            .exclude(sexo='')
            .values('sexo')
            .annotate(cantidad=models.Count('id_paciente'))
        )

        # Diagnóstico preliminar (normalizado en ETL)
        diagnostico = list(
            qs.values('diagnostico_preliminar')
            .exclude(diagnostico_preliminar='')
            .values('diagnostico_preliminar')
            .annotate(cantidad=models.Count('id_paciente'))
            .order_by('-cantidad')[:10]
        )

        # Segmentación por riesgo
        riesgo = list(
            qs.values('riesgo_enfermedad')
            .exclude(riesgo_enfermedad='')
            .annotate(cantidad=models.Count('id_paciente'))
            .order_by('-cantidad')
        )

        # Bins IMC para barras/segmentación
        def imc_bin(v):
            if v is None:
                return None
            try:
                v = float(v)
            except Exception:
                return None
            if v < 18.5:
                return 'Bajo peso'
            if v < 25:
                return 'Normal'
            if v < 30:
                return 'Sobrepeso'
            return 'Obesidad'

        # calcular bins en memoria (dataset 1800 => ok)
        bins = {'Bajo peso': 0, 'Normal': 0, 'Sobrepeso': 0, 'Obesidad': 0}
        for p in qs.only('imc'):
            b = imc_bin(p.imc)
            if b in bins:
                bins[b] += 1

        imc = [{'categoria': k, 'cantidad': v} for k, v in bins.items()]

        # Histograma por edad (buckets)
        buckets = [(0, 17), (18, 29), (30, 44), (45, 59), (60, 120)]
        edad_hist = []
        for lo, hi in buckets:
            c = qs.filter(edad__gte=lo, edad__lte=hi).count()
            edad_hist.append({'rango': f'{lo}-{hi}', 'cantidad': c})

        # Sexo: usar valores para evitar anotación duplicada
        sexo = list(
            qs.values('sexo')
            .exclude(sexo='')
            .annotate(cantidad=models.Count('id_paciente'))
            .order_by('-cantidad')
        )

        return Response({'sexo': sexo, 'riesgo': riesgo, 'diagnostico': diagnostico, 'imc': imc, 'edad': edad_hist})


class PieRiesgoView(APIView):
    """Datos para torta (pie): distribución por riesgo."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Paciente.objects.all()
        data = list(
            qs.values('riesgo_enfermedad')
            .exclude(riesgo_enfermedad='')
            .annotate(cantidad=models.Count('id_paciente'))
            .order_by('-cantidad')
        )
        return Response({'data': data})


class SeriesTendenciasView(APIView):
    """Datos para líneas/tendencias: riesgo por fecha_consulta (conteo)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Paciente.objects.exclude(fecha_consulta__isnull=True)
        series = (
            qs.values('fecha_consulta', 'riesgo_enfermedad')
            .annotate(cantidad=models.Count('id_paciente'))
            .order_by('fecha_consulta')
        )

        # agrupar por riesgo
        buckets = {'Bajo': [], 'Medio': [], 'Alto': [], 'Crítico': []}
        fechas = sorted({r['fecha_consulta'] for r in series})
        for r in series:
            fechas_idx = fechas.index(r['fecha_consulta'])
            # rellenar con 0 si hace falta
            for k in buckets.keys():
                if len(buckets[k]) < len(fechas):
                    buckets[k].extend([0] * (len(fechas) - len(buckets[k])))
            key = r['riesgo_enfermedad']
            if key in buckets:
                buckets[key][fechas_idx] = r['cantidad']

        return Response({'fechas': fechas, 'series': buckets})


class HeatmapView(APIView):
    """Heatmap simple: matriz Riesgo x Sexo (conteos)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Paciente.objects.all()
        riesgos = ['Bajo', 'Medio', 'Alto', 'Crítico']
        sexos = ['M', 'F']

        matrix = {r: {s: 0 for s in sexos} for r in riesgos}
        for r in riesgos:
            for s in sexos:
                matrix[r][s] = qs.filter(riesgo_enfermedad__iexact=r, sexo__iexact=s).count()

        return Response({'riesgos': riesgos, 'sexos': sexos, 'matrix': matrix})


