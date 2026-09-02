from rest_framework import status
from rest_framework.test import APITestCase

from shared.test_factories import make_user


class EscaladaPrivilegiosTests(APITestCase):
    def setUp(self):
        self.asistente = make_user("asis", "ASSISTANT")
        self.admin = make_user("admin", "MANAGER")

    def test_asistente_no_puede_autoascenderse(self):
        self.client.force_authenticate(self.asistente)
        r = self.client.patch(
            f"/api/users/{self.asistente.id}/", {"rol": "ADMIN"}, format="json"
        )
        self.asistente.refresh_from_db()
        # No se rechaza, pero el campo rol es de solo lectura: se ignora.
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(self.asistente.rol, "ASSISTANT")

    def test_admin_si_puede_cambiar_rol(self):
        self.client.force_authenticate(self.admin)
        r = self.client.patch(
            f"/api/users/{self.asistente.id}/", {"rol": "MEDICO"}, format="json"
        )
        self.asistente.refresh_from_db()
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(self.asistente.rol, "MEDICO")

    def test_asistente_solo_se_ve_a_si_mismo(self):
        self.client.force_authenticate(self.asistente)
        r = self.client.get("/api/users/")
        ids = [u["id"] for u in r.data["results"]]
        self.assertEqual(ids, [self.asistente.id])

    def test_no_administrativo_no_crea_usuarios(self):
        self.client.force_authenticate(self.asistente)
        r = self.client.post(
            "/api/users/",
            {"username": "nuevo", "password": "Otra.Clave.2026", "rol": "ADMIN"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
