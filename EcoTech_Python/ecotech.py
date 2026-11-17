"""EcoTech Solutions: implementación didáctica del UML definitivo corregido.

Contiene exactamente las 14 clases principales del diagrama de draw.io.
Las colecciones se guardan en memoria. No es una aplicación de producción.
Requiere Python >= 3.10; PDF y Excel necesitan dependencias opcionales.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from itertools import count
from pathlib import Path
from secrets import token_bytes
from typing import Any
from xml.sax.saxutils import escape
import re


_CORREO = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_ITERACIONES_HASH = 600_000


def _texto(valor: str, campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} no puede estar vacío.")
    return valor.strip()


def _correo_valido(valor: str) -> str:
    correo = _texto(valor, "Correo").lower()
    if not _CORREO.fullmatch(correo):
        raise ValueError("Formato de correo electrónico inválido.")
    return correo


def _decimal_positivo(valor: Any, campo: str, *, cero: bool = False) -> Decimal:
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{campo} debe ser un número válido.") from None
    if not numero.is_finite() or (numero < 0 if cero else numero <= 0):
        raise ValueError(f"{campo} debe ser {'mayor o igual a cero' if cero else 'mayor que cero'}.")
    return numero


def _crear_hash(clave: str) -> str:
    if len(clave) < 12:
        raise ValueError("La contraseña debe tener al menos 12 caracteres.")
    sal = token_bytes(16)
    digest = pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, _ITERACIONES_HASH)
    return f"{sal.hex()}${digest.hex()}"


def _comprobar_hash(clave: str, clave_hash: str) -> bool:
    try:
        sal_hex, digest_hex = clave_hash.split("$", 1)
        sal, esperado = bytes.fromhex(sal_hex), bytes.fromhex(digest_hex)
    except (ValueError, AttributeError):
        return False
    actual = pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, _ITERACIONES_HASH)
    return compare_digest(actual, esperado)


# 1. Usuario y 2. Administrador: generalización (herencia).
class Usuario:
    def __init__(self, id_usuario: int, correo: str, clave: str) -> None:
        self._id_usuario = id_usuario
        self._correo = _correo_valido(correo)
        self._contrasena_hash = _crear_hash(clave)
        self._activo = True
        self._empleado: Empleado | None = None

    @property
    def id_usuario(self) -> int:
        return self._id_usuario

    @property
    def correo(self) -> str:
        return self._correo

    @property
    def empleado(self) -> Empleado | None:
        return self._empleado

    @property
    def activo(self) -> bool:
        return self._activo

    def tiene_permiso(self, accion: str) -> bool:
        return self._activo and accion in {"consultar_proyectos", "registrar_horas"}

    def cambiar_contrasena(self, clave_actual: str, clave_nueva: str) -> None:
        if not _comprobar_hash(clave_actual, self._contrasena_hash):
            raise PermissionError("Contraseña actual incorrecta.")
        self._contrasena_hash = _crear_hash(clave_nueva)

    def _verificar_clave(self, clave: str) -> bool:
        return self._activo and _comprobar_hash(clave, self._contrasena_hash)

    def desactivar(self) -> None:
        self._activo = False


class Administrador(Usuario):
    def tiene_permiso(self, accion: str) -> bool:
        return self.activo and accion in {
            "consultar_proyectos", "registrar_horas", "gestionar", "generar_informes"
        }

    def solicitar_gestion(self, servicio: ServicioGestion, operacion: str, **datos: Any) -> Any:
        """Ejecuta solo operaciones administrativas autorizadas."""
        permitidas = {
            "registrar_empleado", "crear_departamento", "buscar_departamento",
            "eliminar_departamento", "crear_proyecto", "eliminar_proyecto",
            "asignar_proyecto", "finalizar_asignacion", "asignar_departamento",
            "reasignar_empleado", "asignar_gerente", "actualizar_proyecto",
        }
        if not self.tiene_permiso("gestionar") or operacion not in permitidas:
            raise PermissionError("Operación no autorizada.")
        metodo = getattr(servicio, operacion)
        return metodo(actor=self, **datos)

    def solicitar_informe(
        self, generador: GeneradorInforme, tipo: str, exportador: ExportadorInforme,
        ruta: str | Path,
    ) -> Path:
        return generador.generar(tipo, exportador, ruta, actor=self)


# 3. ServicioAutenticacion: acceso a cuentas y comprobación de contraseñas.
class ServicioAutenticacion:
    def __init__(self) -> None:
        self._usuarios: dict[str, Usuario] = {}
        self._ids = count(1)

    def crear_cuenta(
        self, empleado: Empleado, clave: str, *, administrador: bool = False,
        actor: Administrador | None = None,
    ) -> Usuario:
        # Excepción de arranque: el primer usuario tiene que ser administrador.
        if self._usuarios:
            if actor is None or not actor.tiene_permiso("gestionar"):
                raise PermissionError("Solo un administrador puede crear cuentas.")
        elif not administrador:
            raise ValueError("La primera cuenta debe ser de administrador.")
        if empleado.cuenta is not None:
            raise ValueError("Este empleado ya tiene una cuenta de usuario.")
        if empleado.correo in self._usuarios:
            raise ValueError("El correo ya está registrado.")
        clase = Administrador if administrador else Usuario
        usuario = clase(next(self._ids), empleado.correo, clave)
        usuario._empleado = empleado
        empleado._cuenta = usuario
        self._usuarios[usuario.correo] = usuario
        return usuario

    def autenticar(self, correo: str, clave: str) -> Usuario:
        cuenta = self._usuarios.get(_correo_valido(correo))
        if cuenta is None or not cuenta._verificar_clave(clave):
            raise PermissionError("Credenciales inválidas o cuenta desactivada.")
        return cuenta

    def verificar_acceso(self, usuario: Usuario, accion: str) -> bool:
        return usuario.tiene_permiso(accion)


# 4. Empleado: una cuenta opcional y un departamento como máximo.
class Empleado:
    def __init__(
        self, id_empleado: int, nombre: str, direccion: str, telefono: str,
        correo: str, fecha_contrato: date, salario: Decimal | int | str,
    ) -> None:
        self._id_empleado = id_empleado
        self._nombre = _texto(nombre, "Nombre")
        self._direccion = _texto(direccion, "Dirección")
        self._telefono = _texto(telefono, "Teléfono")
        self._correo = _correo_valido(correo)
        self._fecha_contrato = fecha_contrato
        self._salario = _decimal_positivo(salario, "Salario", cero=True)
        self._departamento: Departamento | None = None
        self._cuenta: Usuario | None = None
        self._asignaciones: list[AsignacionProyecto] = []

    @property
    def id_empleado(self) -> int:
        return self._id_empleado

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def correo(self) -> str:
        return self._correo

    @property
    def salario(self) -> Decimal:
        return self._salario

    @property
    def departamento(self) -> Departamento | None:
        return self._departamento

    @property
    def cuenta(self) -> Usuario | None:
        return self._cuenta

    def actualizar_datos(
        self, *, nombre: str | None = None, direccion: str | None = None,
        telefono: str | None = None, salario: Decimal | int | str | None = None,
    ) -> None:
        if nombre is not None:
            self._nombre = _texto(nombre, "Nombre")
        if direccion is not None:
            self._direccion = _texto(direccion, "Dirección")
        if telefono is not None:
            self._telefono = _texto(telefono, "Teléfono")
        if salario is not None:
            self._salario = _decimal_positivo(salario, "Salario", cero=True)

    def consultar_proyectos(self) -> list[Proyecto]:
        return [a.proyecto for a in self._asignaciones if a.esta_activa()]


# 5. Departamento: siempre con un gerente asociado.
class Departamento:
    def __init__(self, id_departamento: int, nombre: str, gerente: Empleado) -> None:
        self._id_departamento = id_departamento
        self._nombre = _texto(nombre, "Nombre de departamento")
        self._gerente = gerente
        self._empleados: list[Empleado] = []
        self.agregar_empleado(gerente)

    @property
    def id_departamento(self) -> int:
        return self._id_departamento

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def gerente(self) -> Empleado:
        return self._gerente

    @property
    def empleados(self) -> tuple[Empleado, ...]:
        return tuple(self._empleados)

    def agregar_empleado(self, empleado: Empleado) -> None:
        if empleado.departamento not in (None, self):
            raise ValueError("El empleado ya pertenece a otro departamento.")
        if empleado not in self._empleados:
            self._empleados.append(empleado)
        empleado._departamento = self

    def quitar_empleado(self, empleado: Empleado) -> None:
        if empleado is self._gerente:
            raise ValueError("Primero debe asignar un nuevo gerente.")
        if empleado in self._empleados:
            self._empleados.remove(empleado)
            empleado._departamento = None

    def asignar_gerente(self, empleado: Empleado) -> None:
        if empleado not in self._empleados:
            raise ValueError("El gerente debe pertenecer al departamento.")
        self._gerente = empleado

    def actualizar_nombre(self, nombre: str) -> None:
        self._nombre = _texto(nombre, "Nombre de departamento")


# 6. Proyecto: agrupa asignaciones.
class Proyecto:
    def __init__(self, id_proyecto: int, nombre: str, descripcion: str, fecha_inicio: date) -> None:
        self._id_proyecto = id_proyecto
        self._nombre = _texto(nombre, "Nombre de proyecto")
        self._descripcion = _texto(descripcion, "Descripción")
        self._fecha_inicio = fecha_inicio
        self._asignaciones: list[AsignacionProyecto] = []

    @property
    def id_proyecto(self) -> int:
        return self._id_proyecto

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def fecha_inicio(self) -> date:
        return self._fecha_inicio

    def actualizar_datos(self, *, nombre: str | None = None, descripcion: str | None = None) -> None:
        if nombre is not None:
            self._nombre = _texto(nombre, "Nombre de proyecto")
        if descripcion is not None:
            self._descripcion = _texto(descripcion, "Descripción")


# 7. AsignacionProyecto: clase intermedia Empleado <-> Proyecto.
class AsignacionProyecto:
    def __init__(
        self, id_asignacion: int, empleado: Empleado, proyecto: Proyecto,
        fecha_asignacion: date,
    ) -> None:
        if fecha_asignacion < proyecto.fecha_inicio:
            raise ValueError("La asignación no puede ser anterior al inicio del proyecto.")
        self._id_asignacion = id_asignacion
        self._empleado = empleado
        self._proyecto = proyecto
        self._fecha_asignacion = fecha_asignacion
        self._fecha_termino: date | None = None
        self._estado = "activa"
        self._registros: list[RegistroTiempo] = []

    @property
    def id_asignacion(self) -> int:
        return self._id_asignacion

    @property
    def empleado(self) -> Empleado:
        return self._empleado

    @property
    def proyecto(self) -> Proyecto:
        return self._proyecto

    @property
    def fecha_asignacion(self) -> date:
        return self._fecha_asignacion

    @property
    def fecha_termino(self) -> date | None:
        return self._fecha_termino

    @property
    def registros(self) -> tuple[RegistroTiempo, ...]:
        return tuple(self._registros)

    def activar(self) -> None:
        if self._fecha_termino is not None:
            raise ValueError("Una asignación terminada no se reactiva; cree otra.")
        self._estado = "activa"

    def finalizar(self, fecha: date) -> None:
        if not self.esta_activa():
            raise ValueError("La asignación ya está finalizada.")
        if fecha < self._fecha_asignacion:
            raise ValueError("La fecha de término no puede ser anterior al inicio.")
        if any(registro.fecha > fecha for registro in self._registros):
            raise ValueError("Existen horas registradas después de esa fecha.")
        self._fecha_termino = fecha
        self._estado = "finalizada"

    def esta_activa(self) -> bool:
        return self._estado == "activa"


# 8. RegistroTiempo: siempre pertenece a una asignación.
class RegistroTiempo:
    def __init__(
        self, id_registro: int, asignacion: AsignacionProyecto,
        fecha: date, horas_trabajadas: Any, descripcion_tarea: str,
    ) -> None:
        self._id_registro = id_registro
        self._asignacion = asignacion
        self._fecha = fecha
        self._horas_trabajadas = self.validar_horas(horas_trabajadas)
        self._descripcion_tarea = _texto(descripcion_tarea, "Descripción de la tarea")

    @property
    def id_registro(self) -> int:
        return self._id_registro

    @property
    def fecha(self) -> date:
        return self._fecha

    @property
    def horas_trabajadas(self) -> Decimal:
        return self._horas_trabajadas

    @property
    def descripcion_tarea(self) -> str:
        return self._descripcion_tarea

    @staticmethod
    def validar_horas(horas: Any) -> Decimal:
        numero = _decimal_positivo(horas, "Horas trabajadas")
        if numero > 24:
            raise ValueError("Un registro no puede exceder 24 horas.")
        return numero


# 9. ServicioGestion: organiza altas, bajas y asignaciones.
class ServicioGestion:
    def __init__(self) -> None:
        self.empleados: dict[int, Empleado] = {}
        self.departamentos: dict[int, Departamento] = {}
        self.proyectos: dict[int, Proyecto] = {}
        self.asignaciones: dict[int, AsignacionProyecto] = {}
        self._ids_empleados = count(1)
        self._ids_departamentos = count(1)
        self._ids_proyectos = count(1)
        self._ids_asignaciones = count(1)

    @staticmethod
    def _exigir_admin(actor: Administrador | None) -> None:
        if not isinstance(actor, Administrador) or not actor.tiene_permiso("gestionar"):
            raise PermissionError("Esta operación requiere un administrador activo.")

    def registrar_empleado(
        self, *, nombre: str, direccion: str, telefono: str, correo: str,
        fecha_contrato: date, salario: Any,
        actor: Administrador | None = None,
    ) -> Empleado:
        # Arranque: se permite registrar solo el primer empleado sin administrador.
        if self.empleados:
            self._exigir_admin(actor)
        correo_normalizado = _correo_valido(correo)
        if any(e.correo == correo_normalizado for e in self.empleados.values()):
            raise ValueError("Ya existe un empleado con ese correo.")
        empleado = Empleado(
            next(self._ids_empleados), nombre, direccion, telefono,
            correo_normalizado, fecha_contrato, salario,
        )
        self.empleados[empleado.id_empleado] = empleado
        return empleado

    def generar_id_empleado(self) -> int:
        """El ID se crea automáticamente al registrar; este método solo ilustra el UML."""
        return next(self._ids_empleados)

    def crear_departamento(
        self, *, nombre: str, gerente: Empleado, actor: Administrador,
    ) -> Departamento:
        self._exigir_admin(actor)
        self._verificar_empleado(gerente)
        if gerente.departamento is not None:
            raise ValueError("El gerente ya pertenece a un departamento.")
        departamento = Departamento(next(self._ids_departamentos), nombre, gerente)
        self.departamentos[departamento.id_departamento] = departamento
        return departamento

    def buscar_departamento(self, *, nombre: str, actor: Administrador) -> list[Departamento]:
        self._exigir_admin(actor)
        busqueda = _texto(nombre, "Búsqueda").casefold()
        return [d for d in self.departamentos.values() if busqueda in d.nombre.casefold()]

    def eliminar_departamento(self, *, departamento: Departamento, actor: Administrador) -> None:
        self._exigir_admin(actor)
        self._verificar_departamento(departamento)
        # Al eliminar el departamento se conserva a sus empleados en la empresa.
        for empleado in departamento.empleados:
            empleado._departamento = None
        departamento._empleados.clear()
        del self.departamentos[departamento.id_departamento]

    def asignar_departamento(
        self, *, empleado: Empleado, departamento: Departamento, actor: Administrador,
    ) -> None:
        self._exigir_admin(actor)
        self._verificar_empleado(empleado)
        self._verificar_departamento(departamento)
        if empleado.departamento is not None and empleado.departamento is not departamento:
            raise ValueError("Debe reasignar al empleado, no duplicar su departamento.")
        departamento.agregar_empleado(empleado)

    def reasignar_empleado(
        self, *, empleado: Empleado, departamento: Departamento, actor: Administrador,
    ) -> None:
        self._exigir_admin(actor)
        self._verificar_empleado(empleado)
        self._verificar_departamento(departamento)
        anterior = empleado.departamento
        if anterior is departamento:
            return
        if anterior and anterior.gerente is empleado:
            raise ValueError("Debe reemplazar al gerente antes de reasignarlo.")
        if anterior:
            anterior.quitar_empleado(empleado)
        departamento.agregar_empleado(empleado)

    def asignar_gerente(
        self, *, departamento: Departamento, gerente: Empleado, actor: Administrador,
    ) -> None:
        self._exigir_admin(actor)
        self._verificar_departamento(departamento)
        self._verificar_empleado(gerente)
        departamento.asignar_gerente(gerente)

    def crear_proyecto(
        self, *, nombre: str, descripcion: str, fecha_inicio: date,
        actor: Administrador,
    ) -> Proyecto:
        self._exigir_admin(actor)
        proyecto = Proyecto(next(self._ids_proyectos), nombre, descripcion, fecha_inicio)
        self.proyectos[proyecto.id_proyecto] = proyecto
        return proyecto

    def actualizar_proyecto(
        self, *, proyecto: Proyecto, actor: Administrador,
        nombre: str | None = None, descripcion: str | None = None,
    ) -> None:
        self._exigir_admin(actor)
        self._verificar_proyecto(proyecto)
        proyecto.actualizar_datos(nombre=nombre, descripcion=descripcion)

    def eliminar_proyecto(self, *, proyecto: Proyecto, actor: Administrador) -> None:
        self._exigir_admin(actor)
        self._verificar_proyecto(proyecto)
        if proyecto._asignaciones:
            raise ValueError("No se puede eliminar un proyecto con historial de asignaciones.")
        del self.proyectos[proyecto.id_proyecto]

    def asignar_proyecto(
        self, *, empleado: Empleado, proyecto: Proyecto,
        fecha_asignacion: date, actor: Administrador,
    ) -> AsignacionProyecto:
        self._exigir_admin(actor)
        self._verificar_empleado(empleado)
        self._verificar_proyecto(proyecto)
        if any(
            asignacion.proyecto is proyecto and asignacion.esta_activa()
            for asignacion in empleado._asignaciones
        ):
            raise ValueError("Ya existe una asignación activa para este empleado y proyecto.")
        asignacion = AsignacionProyecto(
            next(self._ids_asignaciones), empleado, proyecto, fecha_asignacion
        )
        empleado._asignaciones.append(asignacion)
        proyecto._asignaciones.append(asignacion)
        self.asignaciones[asignacion.id_asignacion] = asignacion
        return asignacion

    def finalizar_asignacion(
        self, *, asignacion: AsignacionProyecto, fecha: date, actor: Administrador,
    ) -> None:
        self._exigir_admin(actor)
        if self.asignaciones.get(asignacion.id_asignacion) is not asignacion:
            raise ValueError("La asignación no pertenece a este sistema.")
        asignacion.finalizar(fecha)

    def _verificar_empleado(self, empleado: Empleado) -> None:
        if self.empleados.get(empleado.id_empleado) is not empleado:
            raise ValueError("Empleado no registrado en este sistema.")

    def _verificar_departamento(self, departamento: Departamento) -> None:
        if self.departamentos.get(departamento.id_departamento) is not departamento:
            raise ValueError("Departamento no registrado en este sistema.")

    def _verificar_proyecto(self, proyecto: Proyecto) -> None:
        if self.proyectos.get(proyecto.id_proyecto) is not proyecto:
            raise ValueError("Proyecto no registrado en este sistema.")


# 10. ServicioRegistroTiempo: validación previa a guardar un registro.
class ServicioRegistroTiempo:
    def __init__(self) -> None:
        self.registros: dict[int, RegistroTiempo] = {}
        self._ids = count(1)

    @staticmethod
    def validar_asignacion(asignacion: AsignacionProyecto, usuario: Usuario) -> None:
        if not usuario.activo or not (
            usuario.empleado is asignacion.empleado or usuario.tiene_permiso("gestionar")
        ):
            raise PermissionError("No está autorizado para registrar horas de esta asignación.")
        if not asignacion.esta_activa():
            raise ValueError("No se pueden registrar horas en una asignación finalizada.")

    @staticmethod
    def validar_fecha(fecha: date, asignacion: AsignacionProyecto) -> None:
        if not isinstance(fecha, date) or isinstance(fecha, datetime):
            raise ValueError("La fecha debe ser una fecha válida.")
        if fecha < asignacion.fecha_asignacion or fecha > date.today():
            raise ValueError("La fecha está fuera del período válido de trabajo.")

    @staticmethod
    def validar_horas(horas: Any) -> Decimal:
        return RegistroTiempo.validar_horas(horas)

    def crear_registro(
        self, *, asignacion: AsignacionProyecto, fecha: date,
        horas: Any, descripcion: str, usuario: Usuario,
    ) -> RegistroTiempo:
        self.validar_asignacion(asignacion, usuario)
        self.validar_fecha(fecha, asignacion)
        cantidad = self.validar_horas(horas)
        if any(
            r.fecha == fecha and r.descripcion_tarea.casefold() == descripcion.strip().casefold()
            for r in asignacion.registros
        ):
            raise ValueError("Ya existe un registro con esa fecha y descripción.")
        registro = RegistroTiempo(next(self._ids), asignacion, fecha, cantidad, descripcion)
        asignacion._registros.append(registro)
        self.registros[registro.id_registro] = registro
        return registro


# 11. GeneradorInforme: prepara datos, delega el formato al exportador.
class GeneradorInforme:
    def __init__(self, gestion: ServicioGestion, tiempos: ServicioRegistroTiempo) -> None:
        self._gestion = gestion
        self._tiempos = tiempos

    def informe_empleados(self) -> list[dict[str, Any]]:
        return [
            {
                "ID": e.id_empleado,
                "Nombre": e.nombre,
                "Correo": e.correo,
                "Departamento": e.departamento.nombre if e.departamento else "Sin asignar",
                "Salario": str(e.salario),
            }
            for e in self._gestion.empleados.values()
        ]

    def informe_proyectos(self) -> list[dict[str, Any]]:
        return [
            {
                "ID": p.id_proyecto,
                "Proyecto": p.nombre,
                "Inicio": p.fecha_inicio.isoformat(),
                "Asignaciones": len(p._asignaciones),
            }
            for p in self._gestion.proyectos.values()
        ]

    def informe_departamentos(self) -> list[dict[str, Any]]:
        return [
            {
                "ID": d.id_departamento,
                "Departamento": d.nombre,
                "Gerente": d.gerente.nombre,
                "Empleados": len(d.empleados),
            }
            for d in self._gestion.departamentos.values()
        ]

    def informe_horas(self) -> list[dict[str, Any]]:
        return [
            {
                "ID": r.id_registro,
                "Fecha": r.fecha.isoformat(),
                "Empleado": r._asignacion.empleado.nombre,
                "Proyecto": r._asignacion.proyecto.nombre,
                "Horas": str(r.horas_trabajadas),
                "Tarea": r.descripcion_tarea,
            }
            for r in self._tiempos.registros.values()
        ]

    def generar(
        self, tipo: str, exportador: ExportadorInforme, ruta: str | Path,
        *, actor: Administrador,
    ) -> Path:
        if not isinstance(actor, Administrador) or not actor.tiene_permiso("generar_informes"):
            raise PermissionError("Solo los administradores pueden generar informes.")
        opciones = {
            "empleados": self.informe_empleados,
            "proyectos": self.informe_proyectos,
            "departamentos": self.informe_departamentos,
            "horas": self.informe_horas,
        }
        if tipo not in opciones:
            raise ValueError(f"Tipo de informe desconocido: {tipo}")
        return exportador.exportar(opciones[tipo](), ruta)


# 12. Clase abstracta: contrato común para mostrar polimorfismo.
class ExportadorInforme(ABC):
    @abstractmethod
    def exportar(self, datos: list[dict[str, Any]], ruta: str | Path) -> Path:
        """Genera un archivo con los datos del informe."""


# 13. ExportadorPDF: implementación especializada del contrato.
class ExportadorPDF(ExportadorInforme):
    def exportar(self, datos: list[dict[str, Any]], ruta: str | Path) -> Path:
        try:
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
        except ImportError as error:
            raise RuntimeError("Instala reportlab: python -m pip install reportlab") from error
        archivo = Path(ruta)
        if archivo.suffix.lower() != ".pdf":
            raise ValueError("La ruta de PDF debe terminar en .pdf")
        archivo.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(str(archivo), pagesize=landscape(A4),
                                leftMargin=32, rightMargin=32, topMargin=35, bottomMargin=35)
        estilo = ParagraphStyle("EcoTech", fontName="Helvetica", fontSize=9, leading=12)
        titulo = ParagraphStyle("EcoTechTitulo", parent=estilo, fontSize=16,
                                alignment=TA_CENTER, spaceAfter=16)
        elementos = [Paragraph("EcoTech Solutions · Informe", titulo), Spacer(1, 8)]
        if datos:
            columnas = list(datos[0])
            matriz = [[Paragraph(f"<b>{escape(str(k))}</b>", estilo) for k in columnas]]
            matriz.extend([
                [Paragraph(escape(str(fila.get(k, ""))), estilo) for k in columnas]
                for fila in datos
            ])
            ancho = (landscape(A4)[0] - 64) / len(columnas)
            tabla = Table(matriz, colWidths=[ancho] * len(columnas), repeatRows=1, hAlign="CENTER")
            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
                ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#C1C1C1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F7F7")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elementos.append(tabla)
        else:
            elementos.append(Paragraph("No existen datos para este informe.", estilo))
        doc.build(elementos)
        return archivo


# 14. ExportadorExcel: otra implementación del mismo método exportar().
class ExportadorExcel(ExportadorInforme):
    def exportar(self, datos: list[dict[str, Any]], ruta: str | Path) -> Path:
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            from openpyxl.utils import get_column_letter
        except ImportError as error:
            raise RuntimeError("Instala openpyxl: python -m pip install openpyxl") from error
        archivo = Path(ruta)
        if archivo.suffix.lower() != ".xlsx":
            raise ValueError("La ruta de Excel debe terminar en .xlsx")
        archivo.parent.mkdir(parents=True, exist_ok=True)
        libro = Workbook()
        hoja = libro.active
        hoja.title = "EcoTech"
        if datos:
            columnas = list(datos[0])
            hoja.append(columnas)
            for fila in datos:
                hoja.append([str(fila.get(c, "")) for c in columnas])
                # Evitar que texto proveniente del usuario sea interpretado como fórmula.
                for celda in hoja[hoja.max_row]:
                    celda.data_type = "s"
            for celda in hoja[1]:
                celda.font = Font(bold=True, color="000000")
                celda.fill = PatternFill("solid", fgColor="EAEAEA")
                celda.alignment = Alignment(wrap_text=True)
            for indice, columna in enumerate(hoja.columns, 1):
                largo = max(len(str(c.value or "")) for c in columna)
                hoja.column_dimensions[get_column_letter(indice)].width = min(max(largo + 3, 13), 48)
            hoja.freeze_panes = "A2"
            hoja.auto_filter.ref = hoja.dimensions
        else:
            hoja["A1"] = "Sin datos para mostrar"
        libro.save(archivo)
        return archivo