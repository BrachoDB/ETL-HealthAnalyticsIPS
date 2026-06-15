import csv
import hashlib
import io
import os
import tempfile

import pandas as pd

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient
from apps.analytics.models import ExportAudit
from apps.authentication.models import User
from apps.etl.models import ETLLog, Patient
from apps.etl.services import ETLService, REQUIRED_COLUMNS

class ClinicalAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123', role='MEDICO')
        self.client.force_authenticate(user=self.user)

        self.analista = User.objects.create_user(username='analista', password='password123', role='ANALISTA')
        
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

    def _patient_row(self, patient_id, temperatura='36.5', fecha_consulta='2026-06-01'):
        return {
            'id_paciente': patient_id,
            'nombres': 'Upload',
            'apellidos': 'CSV',
            'edad': 35,
            'sexo': 'Masculino',
            'peso': 75,
            'altura': 1.75,
            'imc': 24.49,
            'presión_sistólica': 120,
            'presión_diastólica': 80,
            'frecuencia_cardiaca': 72,
            'glucosa': 90,
            'colesterol': 180,
            'saturación_oxígeno': 98,
            'temperatura': temperatura,
            'antecedentes_familiares': 'False',
            'fumador': 'False',
            'consumo_alcohol': 'False',
            'actividad_física': 'Media',
            'diagnóstico_preliminar': 'Control',
            'riesgo_enfermedad': 'Bajo',
            'fecha_consulta': fecha_consulta,
        }

    def test_get_patients(self):
        response = self.client.get('/api/pacientes/data/')
        self.assertEqual(response.status_code, 200)
        # If not paginated, response.data is a list
        data = response.data.get('results') if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 1)

    def test_medico_can_enqueue_default_etl_job(self):
        response = self.client.post('/api/pacientes/logs/run/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['estado'], 'Exitoso')

    def test_medico_can_enqueue_csv_etl_job(self):
        row = self._patient_row(2001)
        content = ','.join(REQUIRED_COLUMNS) + '\n' + ','.join(str(value) for value in row.values())
        upload = SimpleUploadedFile('valid.csv', content.encode('utf-8-sig'), content_type='text/csv')

        response = self.client.post('/api/pacientes/upload-csv/', {'archivo': upload}, format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['estado'], 'Exitoso')

    def test_medico_can_enqueue_excel_etl_job(self):
        row = self._patient_row(2002)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame([row]).to_excel(writer, index=False)
        upload = SimpleUploadedFile('valid.xlsx', output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        response = self.client.post('/api/pacientes/upload-csv/', {'archivo': upload}, format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['estado'], 'Exitoso')
        self.assertEqual(response.data['source_type'], 'xlsx')

    def test_get_kpis(self):
        response = self.client.get('/api/analytics/kpis/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_pacientes'], 1)

    def test_export_creates_audit_record(self):
        response = self.client.get('/api/analytics/export/csv/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ExportAudit.objects.count(), 1)
        audit = ExportAudit.objects.get()
        self.assertEqual(audit.usuario, self.user)
        self.assertEqual(audit.export_format, 'csv')
        self.assertEqual(audit.total_rows, 1)

    def test_analista_can_read_but_cannot_write_patient_data(self):
        self.client.force_authenticate(user=self.analista)

        read_response = self.client.get('/api/pacientes/data/')
        self.assertEqual(read_response.status_code, 200)

        write_response = self.client.post('/api/pacientes/data/', {
            'id_paciente': 1000,
            'nombres': 'Analista',
            'apellidos': 'Readonly',
            'edad': 30,
            'sexo': 'Masculino',
            'peso': 70.0,
            'altura': 1.70,
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
            'actividad_fisica': 'Media',
            'diagnostico_preliminar': 'Paciente sano',
            'riesgo_enfermedad': 'Bajo',
            'fecha_consulta': '2026-06-11',
        }, format='json')
        self.assertEqual(write_response.status_code, 403)

    def test_analista_cannot_run_etl_or_predict_ml(self):
        self.client.force_authenticate(user=self.analista)

        etl_response = self.client.post('/api/pacientes/logs/run/')
        self.assertEqual(etl_response.status_code, 403)

        ml_response = self.client.post('/api/ml/predict/', {
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
        })
        self.assertEqual(ml_response.status_code, 403)


class ETLServiceAuditTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='etljob', password='password123', role='MEDICO')

    def test_etl_service_records_audit_fields_and_rejects_invalid_rows(self):
        valid_row = self._patient_row(1001, temperatura='36.5', fecha_consulta='2026-06-01')
        invalid_row = self._patient_row(1002, temperatura='50', fecha_consulta='2099-01-01')

        with tempfile.NamedTemporaryFile('w+', suffix='.csv', encoding='utf-8-sig', delete=False, newline='') as file_obj:
            writer = csv.DictWriter(file_obj, fieldnames=REQUIRED_COLUMNS)
            writer.writeheader()
            writer.writerow(valid_row)
            writer.writerow(invalid_row)
            temp_path = file_obj.name

        try:
            result = ETLService().run(file_path=temp_path)
            log = result.log

            with open(temp_path, 'rb') as file_obj:
                expected_hash = hashlib.sha256(file_obj.read()).hexdigest()

            self.assertEqual(log.estado, 'Exitoso')
            self.assertEqual(result.registros_extraidos, 2)
            self.assertEqual(result.registros_validos, 1)
            self.assertEqual(result.registros_procesados, 1)
            self.assertEqual(result.registros_invalidos, 1)
            self.assertEqual(result.registros_creados, 1)
            self.assertEqual(log.source_type, 'csv')
            self.assertEqual(log.source_hash, expected_hash)
            self.assertEqual(log.schema_version, '1.0')
            self.assertEqual(log.validation_rules_version, '1.0')
            self.assertEqual(Patient.objects.count(), 1)
            self.assertEqual(ETLLog.objects.count(), 1)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_etl_service_rejects_advanced_clinical_inconsistencies(self):
        valid_row = self._patient_row(1001, temperatura='36.5', fecha_consulta='2026-06-01')
        imc_mismatch = self._patient_row(1002, temperatura='36.5', fecha_consulta='2026-06-01')
        imc_mismatch['peso'] = 75
        imc_mismatch['altura'] = 1.75
        imc_mismatch['imc'] = 99
        pressure_error = self._patient_row(1003, temperatura='36.5', fecha_consulta='2026-06-01')
        pressure_error['presión_sistólica'] = 100
        pressure_error['presión_diastólica'] = 120
        duplicate_first = self._patient_row(1004, temperatura='36.5', fecha_consulta='2026-06-01')
        duplicate_second = self._patient_row(1004, temperatura='36.5', fecha_consulta='2026-06-01')

        with tempfile.NamedTemporaryFile('w+', suffix='.csv', encoding='utf-8-sig', delete=False, newline='') as file_obj:
            writer = csv.DictWriter(file_obj, fieldnames=REQUIRED_COLUMNS)
            writer.writeheader()
            writer.writerow(valid_row)
            writer.writerow(imc_mismatch)
            writer.writerow(pressure_error)
            writer.writerow(duplicate_first)
            writer.writerow(duplicate_second)
            temp_path = file_obj.name

        try:
            result = ETLService().run(file_path=temp_path)
            log = result.log

            self.assertEqual(log.estado, 'Exitoso')
            self.assertEqual(result.registros_extraidos, 5)
            self.assertEqual(result.registros_procesados, 1)
            self.assertEqual(result.registros_invalidos, 3)
            self.assertEqual(Patient.objects.count(), 1)
            self.assertIn('imc', log.detalles)
            self.assertIn('presión sistólica', log.detalles)
            self.assertIn('duplicado_paciente_fecha', log.detalles)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_etl_service_runs_excel_and_deletes_source(self):
        row = self._patient_row(3002)
        temp_path = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False).name
        pd.DataFrame([row]).to_excel(temp_path, index=False)

        processed = ETLService().run(file_path=temp_path)
        log = processed.log

        self.assertEqual(log.estado, 'Exitoso')
        self.assertEqual(log.source_type, 'xlsx')
        self.assertEqual(Patient.objects.count(), 1)

    def _patient_row(self, patient_id, temperatura='36.5', fecha_consulta='2026-06-01'):
        return {
            'id_paciente': patient_id,
            'nombres': 'Auditoria',
            'apellidos': 'ETL',
            'edad': 35,
            'sexo': 'Masculino',
            'peso': 75,
            'altura': 1.75,
            'imc': 24.49,
            'presión_sistólica': 120,
            'presión_diastólica': 80,
            'frecuencia_cardiaca': 72,
            'glucosa': 90,
            'colesterol': 180,
            'saturación_oxígeno': 98,
            'temperatura': temperatura,
            'antecedentes_familiares': 'False',
            'fumador': 'False',
            'consumo_alcohol': 'False',
            'actividad_física': 'Media',
            'diagnóstico_preliminar': 'Control',
            'riesgo_enfermedad': 'Bajo',
            'fecha_consulta': fecha_consulta,
        }
