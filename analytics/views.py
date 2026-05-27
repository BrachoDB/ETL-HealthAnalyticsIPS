from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Paciente


class PacienteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Paciente.objects.all()[:200]
        data = [
            {
                'id_paciente': p.id_paciente,
                'nombres': p.nombres,
                'apellidos': p.apellidos,
                'edad': p.edad,
                'sexo': p.sexo,
                'imc': p.imc,
                'riesgo_enfermedad': p.riesgo_enfermedad,
            }
            for p in qs
        ]
        return Response({'results': data, 'count': len(data)})

