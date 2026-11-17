"""Ejecutar: python demo.py

Crea datos de ejemplo y exporta dos informes en la carpeta salida/.
No requiere una base de datos ni conexión a Internet.
"""
from datetime import date, timedelta
from pathlib import Path
from secrets import token_urlsafe

from ecotech import (
    ServicioGestion, ServicioAutenticacion, ServicioRegistroTiempo,
    GeneradorInforme, ExportadorPDF, ExportadorExcel,
)


def main() -> None:
    gestion = ServicioGestion()
    autenticacion = ServicioAutenticacion()
    tiempos = ServicioRegistroTiempo()
    informes = GeneradorInforme(gestion, tiempos)

    # 1. Registrar el primer empleado y crear la cuenta administradora.
    # Solo se permite esta inicialización sin un administrador previo.
    administrador_empleado = gestion.registrar_empleado(
        nombre="Camila Soto", direccion="Santiago, Chile", telefono="+56911111111",
        correo="camila@ecotech.cl", fecha_contrato=date(2025, 3, 1), salario="1250000",
    )
    clave_admin = token_urlsafe(24)
    admin = autenticacion.crear_cuenta(
        administrador_empleado, clave_admin, administrador=True,
    )
    autenticacion.autenticar("camila@ecotech.cl", clave_admin)

    # 2. Registrar empleados a través de una cuenta administradora.
    empleado = admin.solicitar_gestion(
        gestion, "registrar_empleado", nombre="Diego Morales",
        direccion="Providencia, Chile", telefono="+56922222222",
        correo="diego@ecotech.cl", fecha_contrato=date(2026, 1, 15),
        salario="980000",
    )
    usuario_empleado = autenticacion.crear_cuenta(
        empleado, token_urlsafe(24), actor=admin,
    )

    # 3. Crear el departamento; su gerente debe ser empleado de la empresa.
    departamento = admin.solicitar_gestion(
        gestion, "crear_departamento", nombre="Desarrollo Sostenible",
        gerente=administrador_empleado,
    )
    admin.solicitar_gestion(
        gestion, "asignar_departamento", empleado=empleado, departamento=departamento,
    )

    # 4. Crear proyecto y asignar un empleado (muchos-a-muchos resuelto por AsignacionProyecto).
    inicio = date.today() - timedelta(days=10)
    proyecto = admin.solicitar_gestion(
        gestion, "crear_proyecto", nombre="Panel de Energía",
        descripcion="Panel interno para monitorear consumo eléctrico", fecha_inicio=inicio,
    )
    asignacion = admin.solicitar_gestion(
        gestion, "asignar_proyecto", empleado=empleado,
        proyecto=proyecto, fecha_asignacion=inicio,
    )

    # 5. Registrar horas de trabajo con la propia cuenta del empleado.
    registro = tiempos.crear_registro(
        asignacion=asignacion, fecha=date.today(), horas="6.5",
        descripcion="Diseño de la interfaz del panel", usuario=usuario_empleado,
    )

    # 6. Generar informes en dos formatos mediante polimorfismo.
    salida = Path(__file__).parent / "salida"
    pdf = admin.solicitar_informe(
        informes, "horas", ExportadorPDF(), salida / "informe_horas.pdf",
    )
    excel = admin.solicitar_informe(
        informes, "horas", ExportadorExcel(), salida / "informe_horas.xlsx",
    )

    print("=== ECOTECH SOLUTIONS ===")
    print(f"Departamento: {departamento.nombre} | Gerente: {departamento.gerente.nombre}")
    print(f"Empleado: {empleado.nombre} | Proyecto: {proyecto.nombre}")
    print(f"Registro: {registro.horas_trabajadas} horas ({registro.fecha})")
    print(f"PDF generado: {pdf}")
    print(f"Excel generado: {excel}")


if __name__ == "__main__":
    main()