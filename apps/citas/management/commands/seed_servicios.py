"""Carga el catálogo de servicios dentales (idempotente)."""

from django.core.management.base import BaseCommand

from apps.citas.catalog import crear_catalogo


class Command(BaseCommand):
    help = "Crea las categorías y subservicios del catálogo dental."

    def handle(self, *args, **options):
        total = crear_catalogo()
        self.stdout.write(
            self.style.SUCCESS(f"Catálogo cargado: {total} servicios procesados.")
        )
