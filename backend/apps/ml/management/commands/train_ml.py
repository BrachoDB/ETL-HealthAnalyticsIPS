from django.core.management.base import BaseCommand
from apps.ml.training import train_model

class Command(BaseCommand):
    help = 'Entrena el modelo de Machine Learning'

    def handle(self, *args, **options):
        self.stdout.write('Entrenando modelo...')
        metrics = train_model()
        if metrics:
            self.stdout.write(self.style.SUCCESS(f"Modelo entrenado exitosamente. Accuracy: {metrics['accuracy']:.4f}"))
        else:
            self.stdout.write(self.style.ERROR("Error al entrenar el modelo."))
