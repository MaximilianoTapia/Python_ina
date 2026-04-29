# Bucles en Python
# nombre: Maximiliano Tapia

# ejercicio 1: calcular un producto de una serie de enteros hasta que se introduzca un cero

#producto = 1
#while True:
#    numero = int(input("introduce un numero (0 para terminar el ciclo)"))
#    if numero == 0:
#        break
#    producto *= numero
#    print("producto actual:", producto)

# ejercicio 2: calcular la suma de los enteros del 1 al 10

#suma = 0
#for I in range(1, 11):
#    suma += I
#    print("suma actual:", suma)

# ejercicio 3: calcular el producto de los enteros del 1 al 10. indicacion: igual que el ejercicicio 2 pero multliplicando

#producto = 1
#for I in range(1, 11):
#    producto *= I
#    print("producto actual:", producto)

#ejercicio 4: calcular la suma de los pares del 1 al 20. indicacion: parecido al ejercicio 2: cambbia el incremento de valor a sumar y la condicion del bucle while

#suma_pares = 0
#for i in range(1, 21):
#    if i % 2 == 0:
#        suma_pares += i
#        print("suma actual de pares:", suma_pares)

# ejercicio 5:Calcular el factorial de un entero positivo. Indicación: igual que el ejercicio 4 pero la condición de fin del bucle será que elvalor a multiplicar sea menor o igual que el valor del entero positivo dado para calcular su factorial

#factorial = 1
#numero = int(input("introduce un entero positivo para calcular el factorial:"))
#for i in range(1, numero +1):
#    factorial *= i
#    print("factorial actual:", factorial)

#ejercicio 6: Contar cuantos enteros positivos introduce el usuario. Indicación: leer los números mientras sean positivos, usando una variablecontadora que se va incrementando en uno cada vez que se lee un número; elresultado será el valor de esa variable contadora.

#contador = 0
#while True:
#    numero = int(input("introduce un numero positivo o un nnumero negativo para terminar"))
#    if numero < 0:
#            break
#    contador += 1
#    print("contador actual:", contador)

#ejercicio 7:Calcular la media de una serie de enteros positivos; el programa termina cuando seintroduce un cero o un negativo. Indicación: sumar los números y dividir por el número de números (tendrás quellevar la cuenta según el ejercicio 6).

#suma = 0
#contador = 0
#while True:
#    numero = int(input("Introduce un numero positivo o un numero negativo para terminar"))
#    if numero < 0:
#        break
#    suma += numero
#    contador += 1
#    print("suma actual:", suma)
#    if contador > 0:
#        media = suma / contador
#        print("media actual:", media)

#ejercicio 8:Realiza el ejercicio 7 pero preguntando a priori cuantos números se van a introducir. Indicación: Primero habrá que preguntar al usuario cuántos números va aintroducir (variable ‘cuantos’). Tendrás que llevar la cuenta de cuantos números sehan introducido (variable ‘contador’). La condición del bucle es que ‘contador’ sea menor que cuantos

#suma = 0
#contador = 0
#cuantos = int(input("¿cuantos numeros vas a introducir?"))
#while contador < cuantos:
#    numeros = int(input("Introduce un numero positivo:"))
#    suma += numeros
#    contador += 1
#print("suma total:", suma)

#ejercicio 9: Realiza el ejercicio 7, controlando además que cada número que se da es entero positivo. Indicación: para cada número dado tendrás que usar el bucle ‘while’

#suma = 0
#contador = 0
#while True:
#    numero = int(input("Introduce un numero positivo o un numero negativo para terminar"))
#    if numero < 0:
#        break
#    while numero <= 0:
#        print("El numero debe ser positivo. Intentalo de nuevo.")
#        numero = int(input("Introduce un numero positivo o un numero negativo para terminar"))
#    suma += numero
#    contador += 1
#    print("suma actual:", suma)
#        if contador > 0:
#        media = suma / contador
#        print("media actual:", media)

#ejercicio 10: Realizar un programa que calcule la serie numérica de Fibonacci, para N números ingresados previamente. 

#N = int(input("cuantos numeros de la serie de Fibonacci quieres calcular?"))
#a, b = 0, 1
#for i in range(N):
#    print(a)
#    a, b = b, a + b