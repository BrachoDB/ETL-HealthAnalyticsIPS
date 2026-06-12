import pandas as pd
from django import forms


REQUIRED_COLUMNS = [
    'id_paciente',
    'nombres',
    'apellidos',
    'edad',
    'sexo',
    'peso',
    'altura',
    'presión_sistólica',
    'presion_diastolica',
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
    archivo = forms.FileField(label='Archivo CSV clínico')

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if not archivo:
            return archivo

        if not archivo.name.lower().endswith('.csv'):
            raise forms.ValidationError('Solo se permiten archivos con extensión .csv.')

        try:
            archivo.seek(0)
            header = pd.read_csv(archivo, nrows=0, encoding='utf-8-sig').columns.tolist()
        except Exception as exc:
            raise forms.ValidationError(f'No fue posible leer el archivo CSV: {exc}')
        finally:
            archivo.seek(0)

        missing = [column for column in REQUIRED_COLUMNS if column not in header]
        if missing:
            raise forms.ValidationError(f'Columnas faltantes: {", ".join(missing)}')

        return archivo
