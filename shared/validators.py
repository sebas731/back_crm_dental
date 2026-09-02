"""Validadores reutilizables para subida de archivos y documentos."""

from rest_framework import serializers

# Tipos permitidos para adjuntos clínicos y comprobantes.
EXTENSIONES_PERMITIDAS = {
    "pdf", "jpg", "jpeg", "png", "webp", "heic", "gif", "bmp", "tiff",
}
MAX_MB = 10


def validar_archivo(archivo, extensiones=EXTENSIONES_PERMITIDAS, max_mb=MAX_MB):
    """Valida extensión y tamaño de un archivo subido. Devuelve el archivo."""
    if archivo in (None, ""):
        return archivo
    nombre = getattr(archivo, "name", "") or ""
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if ext not in extensiones:
        permitidas = ", ".join(sorted(extensiones))
        raise serializers.ValidationError(
            f"Tipo de archivo no permitido (.{ext or '?'}). "
            f"Usá: {permitidas}."
        )
    size = getattr(archivo, "size", 0) or 0
    if size > max_mb * 1024 * 1024:
        raise serializers.ValidationError(
            f"El archivo supera el máximo de {max_mb} MB."
        )
    return archivo
