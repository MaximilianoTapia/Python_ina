"""Pruebas unitarias de las asociaciones y reglas del UML."""
import unittest
from datetime import date, timedelta
from secrets import token_urlsafe

from ecotech import (
    Administrador, ServicioGestion, ServicioAutenticacion,
    ServicioRegistroTiempo, GeneradorInforme, ExportadorInforme,
)


class TestEcoTech(unittest.TestCase):
    def setUp(self):
        self.gestion = ServicioGestion()
        self.auth = ServicioAutenticacion()
        self.tiempos = ServicioRegistroTiempo()
        self.inicio = date.today() - timedelta(days=6)
        self.jefa = self.gestion.registrar_empleado(
            nombre="Jefa", direccion="Santiago", telefono="111111111",
            correo="jefa@ecotech.cl", fecha_contrato=self.inicio, salario=1000,
        )
        self.clave_admin = token_urlsafe(24)
        self.admin = self.auth.crear_cuenta(
            self.jefa, self.clave_admin, administrador=True,
        )
        self.empleado = self.gestion.registrar_empleado(
            nombre="Analista", direccion="Santiago", telefono="222222222",
            correo="analista@ecotech.cl", fecha_contrato=self.inicio, salario=900,
            actor=self.admin,
        )
        self.clave_empleado = token_urlsafe(24)
        self.cuenta = self.auth.crear_cuenta(
            self.empleado, self.clave_empleado, actor=self.admin,
        )
        self.departamento = self.gestion.crear_departamento(
            nombre="Investigación", gerente=self.jefa, actor=self.admin,
        )
        self.gestion.asignar_departamento(
            empleado=self.empleado, departamento=self.departamento, actor=self.admin,
        )
        self.proyecto = self.gestion.crear_proyecto(
            nombre="Proyecto A", descripcion="Descripción", fecha_inicio=self.inicio,
            actor=self.admin,
        )
        self.asignacion = self.gestion.asignar_proyecto(
            empleado=self.empleado, proyecto=self.proyecto,
            fecha_asignacion=self.inicio, actor=self.admin,
        )

    def test_herencia_y_acceso(self):
        self.assertIsInstance(self.admin, Administrador)
        self.assertTrue(self.auth.verificar_acceso(self.admin, "gestionar"))
        self.assertFalse(self.auth.verificar_acceso(self.cuenta, "gestionar"))
        with self.assertRaises(PermissionError):
            self.gestion.crear_proyecto(
                nombre="X", descripcion="Y", fecha_inicio=self.inicio, actor=self.cuenta,
            )

    def test_cuenta_unica_por_empleado(self):
        with self.assertRaises(ValueError):
            self.auth.crear_cuenta(self.empleado, token_urlsafe(24), actor=self.admin)

    def test_departamento_y_gerente(self):
        self.assertIs(self.departamento.gerente, self.jefa)
        self.assertIs(self.empleado.departamento, self.departamento)
        with self.assertRaises(ValueError):
            self.gestion.crear_departamento(
                nombre="Otro", gerente=self.jefa, actor=self.admin,
            )

    def test_asignacion_duplicada(self):
        with self.assertRaises(ValueError):
            self.gestion.asignar_proyecto(
                empleado=self.empleado, proyecto=self.proyecto,
                fecha_asignacion=self.inicio, actor=self.admin,
            )

    def test_registro_horas(self):
        registro = self.tiempos.crear_registro(
            asignacion=self.asignacion, fecha=date.today(), horas="4.5",
            descripcion="Análisis", usuario=self.cuenta,
        )
        self.assertEqual(str(registro.horas_trabajadas), "4.5")
        self.assertEqual(len(self.asignacion.registros), 1)
        with self.assertRaises(ValueError):
            self.tiempos.crear_registro(
                asignacion=self.asignacion, fecha=date.today(), horas=25,
                descripcion="Error", usuario=self.cuenta,
            )

    def test_fecha_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            self.tiempos.crear_registro(
                asignacion=self.asignacion, fecha=self.inicio - timedelta(days=1),
                horas=3, descripcion="Antes del inicio", usuario=self.cuenta,
            )

    def test_no_registra_en_asignacion_finalizada(self):
        self.gestion.finalizar_asignacion(
            asignacion=self.asignacion, fecha=date.today(), actor=self.admin,
        )
        with self.assertRaises(ValueError):
            self.tiempos.crear_registro(
                asignacion=self.asignacion, fecha=date.today(), horas=1,
                descripcion="Tarde", usuario=self.cuenta,
            )

    def test_reportes(self):
        informes = GeneradorInforme(self.gestion, self.tiempos)
        filas = informes.informe_departamentos()
        self.assertEqual(filas[0]["Gerente"], "Jefa")
        self.assertEqual(filas[0]["Empleados"], 2)
        self.assertEqual(informes.informe_proyectos()[0]["Asignaciones"], 1)

    def test_polimorfismo_abstracto(self):
        with self.assertRaises(TypeError):
            ExportadorInforme()

    def test_autenticacion(self):
        self.assertIs(self.auth.autenticar("analista@ecotech.cl", self.clave_empleado), self.cuenta)
        with self.assertRaises(PermissionError):
            self.auth.autenticar("analista@ecotech.cl", "clave incorrecta")


if __name__ == "__main__":
    unittest.main()
