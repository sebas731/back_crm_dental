from rest_framework import status
from rest_framework.test import APITestCase

from shared.test_factories import make_medico, make_paciente, make_user


class CitaReglasTests(APITestCase):
    def setUp(self):
        self.admin = make_user("admin", "MANAGER")
        self.medico_user = make_user("medico", "MEDICO")
        self.medico = make_medico(usuario=self.medico_user)
        self.paciente = make_paciente()
        self.base = {
            "medico": str(self.medico.id),
            "paciente": str(self.paciente.id),
            "fecha": "2031-05-10",
            "hora_inicio": "09:00",
            "estado": "PROGRAMADA",
        }

    def test_no_permite_doble_reserva(self):
        self.client.force_authenticate(self.admin)
        r1 = self.client.post("/api/citas/", self.base, format="json")
        r2 = self.client.post("/api/citas/", self.base, format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_permite_crear_atendida_sin_atencion(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(
            "/api/citas/", {**self.base, "estado": "ATENDIDA"}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_medico_no_puede_crear_citas(self):
        self.client.force_authenticate(self.medico_user)
        r = self.client.post("/api/citas/", self.base, format="json")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
