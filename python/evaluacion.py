# Evaluación de Calculo de RUT
# Nombre: [Maximiliano Tapia]
# Fecha: [15-Abr-2026]

def calcular_digito_verificador(cuerpo, mostrar=False):
    suma = 0
    multiplicador = 2
    if mostrar:
        print("\nCÁLCULO")
    for digito in reversed(cuerpo):
        resultado = int(digito) * multiplicador
        if mostrar:
            print(f"{digito} x {multiplicador} = {resultado}")
        suma += resultado
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    if mostrar:
        print("Suma total:", suma)
    resta = suma % 11
    if mostrar:
        print("Resta", resta)
    dv = 11 - resta
    if dv == 11:
        return "0"
    elif dv == 10:
        return "K"
    else:
        return str(dv)


def validar_rut(rut, mostrar=False):
    rut = rut.replace(".", "").replace("-", "").replace(" ", "").strip()
    if len(rut) < 2:
        return False
    cuerpo = rut[:-1]
    dv_ingresado = rut[-1].upper()
    if not cuerpo.isdigit():
        return False
    dv_calculado = calcular_digito_verificador(cuerpo, mostrar)
    if mostrar:
        print("DV calculado:", dv_calculado)
        print("DV ingresado:", dv_ingresado)
    return dv_calculado == dv_ingresado


rut_usuario = input("Ingrese su RUT: ").strip()

if validar_rut(rut_usuario, mostrar=True):
    print("\nRUT válido")
else:
    print("\nRUT inválido")