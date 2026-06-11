from django.test import TestCase
from rest_framework.test import APIClient
from apps.authentication.models import User
from apps.etl.models import Patient

class ClinicalAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123', role='MEDICO')
        self.client.force_authenticate(user=self.user)
        
        # Create a sample patient
        Patient.objects.create(
            id_paciente=999,
            nombres='Test',
            apellidos='User',
            edad=30,
            sexo='Masculino',
            peso=70.0,
            altura=1.70,
            imc=24.22,
            presion_sistolica=120,
            presion_diastolica=80,
            frecuencia_cardiaca=70,
            glucosa=90.0,
            colesterol=180.0,
            saturacion_oxigeno=98.0,
            temperatura=36.5,
            antecedentes_familiares=False,
            fumador=False,
            consumo_alcohol=False,
            actividad_fisica='Media',
            diagnostico_preliminar='Paciente sano',
            riesgo_enfermedad='Bajo',
            fecha_consulta='2026-06-11'
        )

    def test_get_patients(self):
        response = self.client.get('/api/pacientes/data/')
        self.assertEqual(response.status_code, 200)
        # If not paginated, response.data is a list
        data = response.data.get('results') if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 1)

    def test_get_kpis(self):
        response = self.client.get('/api/analytics/kpis/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_pacientes'], 1)
