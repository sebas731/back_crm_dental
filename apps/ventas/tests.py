from rest_framework import status
from rest_framework.test import APITestCase

from shared.test_factories import make_paciente, make_user, make_venta_con_cuota


class CobranzaIntegridadTests(APITestCase):
    def setUp(self):
        self.admin = make_user("admin", "MANAGER")
        self.asistente = make_user("asis", "ASSISTANT")
        self.paciente = make_paciente()
        self.venta, self.cuota = make_venta_con_cuota(self.paciente, "100.00")

    def test_cuota_estado_es_solo_lectura(self):
        self.client.force_authenticate(self.admin)
        r = self.client.patch(
            f"/api/cuotas/{self.cuota.id}/", {"estado": "PAGADO"}, format="json"
        )
        self.cuota.refresh_from_db()
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cuota.estado, "PENDIENTE")

    def test_pago_negativo_rechazado(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(
            "/api/pagos/",
            {"cuota": str(self.cuota.id), "monto": "-10.00", "metodo": "EFECTIVO"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pago_excede_saldo_rechazado(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(
            "/api/pagos/",
            {"cuota": str(self.cuota.id), "monto": "200.00", "metodo": "EFECTIVO"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_asistente_no_registra_pago(self):
        self.client.force_authenticate(self.asistente)
        r = self.client.post(
            "/api/pagos/",
            {"cuota": str(self.cuota.id), "monto": "10.00", "metodo": "EFECTIVO"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_descuento_mayor_a_100_rechazado(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(
            "/api/descuentos/",
            {"venta": str(self.venta.id), "tipo": "PORCENTAJE", "valor": "150"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validar_pago_es_idempotente(self):
        self.client.force_authenticate(self.admin)
        pago = self.client.post(
            "/api/pagos/",
            {"cuota": str(self.cuota.id), "monto": "50.00", "metodo": "EFECTIVO"},
            format="json",
        ).data
        r1 = self.client.post(f"/api/pagos/{pago['id']}/validar/")
        r2 = self.client.post(f"/api/pagos/{pago['id']}/validar/")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        # El validador y la fecha no se reescriben en la segunda llamada.
        self.assertEqual(r1.data["validado_por"], r2.data["validado_por"])
        self.assertEqual(r1.data["fecha_validacion"], r2.data["fecha_validacion"])
