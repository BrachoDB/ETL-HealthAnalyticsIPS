from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Avg, StdDev
from apps.etl.models import Patient

class KPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_pacientes = Patient.objects.count()
        if total_pacientes == 0:
            return Response({'error': 'No hay datos'}, status=404)
            
        # Distribución de riesgo
        riesgo_dist = Patient.objects.values('riesgo_enfermedad').annotate(count=Count('id'))
        
        # Pacientes críticos
        criticos = Patient.objects.filter(riesgo_enfermedad='Crítico').count()
        
        # Hipertensos (Sistólica > 140 o Diastólica > 90)
        hipertensos = Patient.objects.filter(presion_sistolica__gt=140).count() # simplificado
        
        # Diabéticos (Glucosa > 126)
        diabeticos = Patient.objects.filter(glucosa__gt=126).count()
        
        # IMC Promedio
        imc_avg = Patient.objects.aggregate(avg_imc=Avg('imc'))['avg_imc']
        
        return Response({
            'total_pacientes': total_pacientes,
            'riesgo_distribucion': list(riesgo_dist),
            'pacientes_criticos': criticos,
            'hipertensos': hipertensos,
            'diabeticos': diabeticos,
            'imc_promedio': imc_avg
        })
