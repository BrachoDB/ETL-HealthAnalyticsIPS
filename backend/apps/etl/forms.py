import pandas as pd
from django import forms
from pathlib import Path


REQUIRED_COLUMNS = [
    'id_paciente',
    'nombres',
    'apellidos',
    'edad',
    'sexo',
    'peso',
    'altura',
    'imc',
    'presión_sistólica',
    'presión_diastólica',
    'frecuencia_cardiaca',
    'glucosa',
    'colesterol',
    'saturación_oxígeno',
    'temperatura',
    'antecedentes_familiares',
    'fumador',
    'consumo_alcohol',
    'actividad_física',
    'diagnóstico_preliminar',
    'riesgo_enfermedad',
    'fecha_consulta',
]


class UploadCSVForm(forms.Form):
    archivo = forms.FileField(label='Archivo clínico CSV o Excel')
    allowed_extensions = {'.csv', '.xlsx', '.xls'}

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if not archivo:
            return archivo

        extension = Path(archivo.name.lower()).suffix
        if extension not in self.allowed_extensions:
            raise forms.ValidationError('Solo se permiten archivos con extensión .csv, .xlsx o .xls.')

        try:
            archivo.seek(0)
            if extension == '.csv':
                header = pd.read_csv(archivo, nrows=0, encoding='utf-8-sig').columns.tolist()
            else:
                header = pd.read_excel(archivo, nrows=0).columns.tolist()
            header = self._normalize_columns(header)
        except Exception as exc:
            raise forms.ValidationError(f'No fue posible leer el archivo clínico: {exc}')
        finally:
            archivo.seek(0)

        missing = [column for column in REQUIRED_COLUMNS if column not in header]
        if missing:
            raise forms.ValidationError(f'Columnas faltantes: {", ".join(missing)}')

        return archivo

    def _normalize_columns(self, columns):
        normalized = []
        for column in columns:
            key = str(column).strip().lower()
            if key == 'imc':
                normalized.append('imc')
            elif 'sist' in key:
                normalized.append('presión_sistólica')
            elif 'diast' in key:
                normalized.append('presión_diastólica')
            elif 'satur' in key and 'ox' in key:
                normalized.append('saturación_oxígeno')
            elif 'diagn' in key:
                normalized.append('diagnóstico_preliminar')
            elif 'activ' in key:
                normalized.append('actividad_física')
            else:
                normalized.append(column)
        return normalized
