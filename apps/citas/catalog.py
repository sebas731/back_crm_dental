"""
Catálogo de servicios/tratamientos dentales de DENTAL SAC.

Estructura: categoría (padre) -> lista de subservicios.
`crear_catalogo()` lo carga de forma idempotente (get_or_create).
"""

from apps.citas.models import ServicioDental

CATALOGO: dict[str, list[str]] = {
    "Ortodoncia y Ortopedia Maxilar": [
        "Ortodoncia fija convencional (brackets metálicos)",
        "Ortodoncia estética (brackets de zafiro, cerámica o resina)",
        "Ortodoncia autoligable",
        "Ortodoncia invisible (alineadores invisibles)",
        "Retenedores fijos o removibles",
        "Cuota de ortodoncia",
        "Reposiciones",
        "Otros",
    ],
    "Odontología General y Preventiva": [
        "Limpieza dental (profilaxis o detartraje)",
        "Curaciones simples",
        "Curaciones compuestas",
    ],
    "Cirugía Oral y Maxilofacial": [
        "Exodoncia simple (extracción quirúrgica menor)",
        "Exodoncia de muelas del juicio (terceros molares retenidos o impactados)",
    ],
    "Implantología Dental": [
        "Colocación de implantes dentales (fijación del perno o tornillo)",
        "Injerto óseo (regeneración ósea guiada)",
    ],
    "Periodoncia": [
        "Raspado y alisado radicular",
        "Gingivectomía",
        "Gingivoplastia",
    ],
    "Endodoncia": [
        "Extracción del nervio infectado, desinfección y sellado",
        "Endodoncia (Varian Doctores)",
    ],
    "Rehabilitación Oral y Prótesis Dental": [
        "Coronas dentales",
        "Carillas de resina",
        "Carillas de porcelana / cerámica",
        "Puentes dentales fijos",
        "Prótesis parciales removibles",
        "Prótesis completa",
    ],
    "Odontología Estética y Diseño de Sonrisa": [
        "Blanqueamiento dental convencional",
        "Blanqueamiento dental a láser",
    ],
    "Odontopediatría": [
        "Curaciones en dientes temporales",
    ],
}


def crear_catalogo() -> int:
    """Crea categorías y subservicios. Devuelve la cantidad total procesada."""
    total = 0
    for categoria, subservicios in CATALOGO.items():
        padre, _ = ServicioDental.objects.get_or_create(
            nombre=categoria, padre__isnull=True
        )
        total += 1
        for nombre in subservicios:
            ServicioDental.objects.get_or_create(nombre=nombre, padre=padre)
            total += 1
    return total
