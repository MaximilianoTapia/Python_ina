# EcoTech Solutions — UML definitivo en Python

Esta es una **implementación didáctica** del último diagrama de clases UML corregido en draw.io, manteniendo sus **14 clases**. El objetivo es mostrar cómo se transforma un modelo conceptual en objetos, métodos, asociaciones, herencia y polimorfismo reales.

## Archivos

- `ecotech.py`: las 14 clases del UML y sus métodos.
- `demo.py`: caso de uso ejecutable (alta de empleados, departamentos, proyectos, horas e informes).
- `test_ecotech.py`: pruebas automáticas con `unittest`.
- `requirements.txt`: librerías para generar PDF y Excel.
- `UML_definitivo_corregido.mmd`: código Mermaid del diagrama corregido, editable en draw.io.

## Ejecutar con Python 3.10 o superior

Abre la carpeta en VS Code o en una terminal:

```bash
python -m pip install -r requirements.txt
python demo.py
```

Se crea `salida/informe_horas.pdf` y `salida/informe_horas.xlsx`.

Para probar las reglas y cardinalidades:

```bash
python -m unittest -v test_ecotech.py
```

Si estás en NixOS, ejecuta los comandos dentro de un entorno Python donde puedas instalar o incluir `reportlab` y `openpyxl`, por ejemplo un entorno virtual o un entorno definido con Nix.

## ¿Dónde están las 14 clases?

| Parte del UML | Clases Python |
| --- | --- |
| Acceso | `Usuario`, `Administrador`, `ServicioAutenticacion` |
| Personal | `Empleado`, `Departamento` |
| Gestión de trabajo | `Proyecto`, `AsignacionProyecto`, `RegistroTiempo` |
| Lógica de negocio | `ServicioGestion`, `ServicioRegistroTiempo` |
| Reportes | `GeneradorInforme`, `ExportadorInforme`, `ExportadorPDF`, `ExportadorExcel` |

## Cardinalidades y reglas representadas

- **Empleado — Usuario (1 a 0..1):** una cuenta pertenece a un empleado; un empleado puede tener cero o una cuenta.
- **Departamento — Empleado (0..1 a 0..*):** cada empleado pertenece como máximo a un departamento, y un departamento admite muchos empleados.
- **Departamento — Gerente (0..1 a 1):** cada departamento creado tiene exactamente un gerente; un empleado no puede dirigir simultáneamente varios departamentos en esta implementación.
- **Empleado — AsignacionProyecto (1 a 0..*):** una asignación corresponde a un empleado, que puede tener varias asignaciones.
- **Proyecto — AsignacionProyecto (1 a 0..*):** una asignación corresponde a un proyecto, que puede tener varios empleados.
- **AsignacionProyecto — RegistroTiempo (1 a 0..*):** un registro corresponde a una asignación y puede haber múltiples registros por asignación.

El UML no define **cómo persistir en una base de datos** ni una interfaz de usuario detallada. Por eso, en esta versión los datos quedan **en memoria** y se pierden al cerrar Python. La generación de PDF/Excel produce archivos reales.

## Buenas prácticas demostradas

- **Encapsulamiento:** los atributos internos usan `_nombre`, `_salario`, etc. y se accede a ellos mediante propiedades/métodos. Python no impide absolutamente el acceso a `_atributo`, pero indica que no se debe modificar externamente.
- **Herencia:** `Administrador(Usuario)`.
- **Polimorfismo:** `ExportadorPDF` y `ExportadorExcel` implementan el mismo método `exportar` de la clase abstracta `ExportadorInforme`.
- **Responsabilidades:** `ServicioGestion` maneja altas y asignaciones, `ServicioRegistroTiempo` valida horas, `ServicioAutenticacion` autentica y `GeneradorInforme` prepara datos.

## Límites de este prototipo

No es una solución lista para producción: faltan una base de datos, permisos granulares, auditoría, controles de privacidad, manejo de sesiones, protección de datos en reposo y una interfaz. Las contraseñas se guardan como derivaciones PBKDF2 con sal aleatoria, no en texto plano, pero el ejemplo no sustituye una revisión de seguridad real. Los datos de prueba son **ficticios** y la demostración genera contraseñas aleatorias en cada ejecución.