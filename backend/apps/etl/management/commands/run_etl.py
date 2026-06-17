from django.core.management.base import BaseCommand

from apps.etl.services import ETLService


class Command(BaseCommand):
    help = 'Ejecuta el proceso ETL para cargar datos clínicos desde Excel o CSV a MySQL'

    def add_arguments(self, parser):
        parser.add_argument('--file', dest='file_path', type=str, help='Ruta del archivo Excel o CSV a procesar')
        parser.add_argument('--user-id', dest='user_id', type=int, help='ID del usuario que ejecuta el ETL')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando proceso ETL...'))
        result = ETLService().run(
            file_path=options.get('file_path'),
            user_id=options.get('user_id'),
        )
        log = result.log

        if log.estado == 'Exitoso':
            self.stdout.write(
                self.style.SUCCESS(
                    f"ETL finalizado. {result.registros_procesados} registros cargados en {log.tiempo_ejecucion:.2f}s"
                )
            )
        else:
            self.stdout.write(self.style.ERROR(f'Error en ETL: {log.detalles}'))
