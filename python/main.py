#Determinar si una palabra es un palíndromo o no.

#palabra = input("Ingrese una palabra:")
#if es_palindromo(palabra):
#else:
#    print("la palabra no es un palindromo")

#Hacer un relog de arena utilizando la función time.sleep() para simular el paso del tiempo.
import time
def reloj_de_arena(tiempo):
    for i in range(tiempo, 0, -1):
        print(f"Tiempo restante: {i} segundos")
        time.sleep(1)
    print("¡El tiempo se ha agotado!")
tiempo = int(input("Ingrese el tiempo en segundos para el reloj de arena: "))
reloj_de_arena(tiempo)