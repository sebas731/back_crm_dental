from rest_framework import status
from rest_framework.test import APITestCase

from shared.test_factories import (
    make_cita,
    make_historia,
    make_medico,
    make_paciente,
    make_user,
)


class RBACClinicoTests(APITestCase):
    def setUp(self):
        self.admin = make_user("admin", "MANAGER")
        self.medico_user = make_user("medico", "MEDICO")
        self.paciente = make_paciente()

    def test_medico_no_puede_borrar_historia(self):
        historia = make_historia(self.paciente)
        self.client.force_authenticate(self.medico_user)
        r = self.client.delete(f"/api/historias-clinicas/{historia.id}/")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_borrar_paciente_con_cita_devuelve_400(self):
        medico = make_medico()
        make_cita(medico, self.paciente)
        self.client.force_authenticate(self.admin)
        r = self.client.delete(f"/api/pacientes/{self.paciente.id}/")
        # ProtectedError -> 400 legible (no 500).
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class DocumentoDniTests(APITestCase):
    def setUp(self):
        self.admin = make_user("admin", "MANAGER")
        self.client.force_authenticate(self.admin)

    def test_dni_con_formato_invalido_es_rechazado(self):
        r = self.client.post(
            "/api/pacientes/",
            {
                "nombre": "Ana",
                "apellido": "Gómez",
                "nombres": "Ana",
                "apellido_paterno": "Gómez",
                "sexo": "F",
                "tipo_documento": "DNI",
                "numero_documento": "123",  # DNI debe tener 8 dígitos
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("numero_documento", r.data)
