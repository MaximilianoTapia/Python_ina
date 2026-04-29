#ejercicio1 : Una empresa de transporte, requiere realizar una proyeccion para el consumo de combustible de su flota. el sistema consiste; 
# 1 el usuario ingresa el rendimiento del vehiculo, en km/its- 
# 2. el usuario ingresa la posicion de origen y destino; en formato GPS DD: 
# 3. el sistema calcula la distancia entre origen y destino, obteniendo la distancia en kilometros. 1° ~111 km. 
# Nota: no considerar la curvatura de la tierra, ni la distancia de los polos. 
# 4: el sistema entrega la cantidad de litros y el valor total de combustible a utilizar

class Trasnporte:
    def __init__(self, rendimiento, origen, destino):
        self.rendimiento = rendimiento
        self.origen = origen
        self.destino = destino

    def calcular_distancia(self):
        lat1, lon1 = map(float, self.origen.split(':'))
        lat2, lon2 = map(float, self.destino.split(':'))
        distancia = ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111
        return distancia

    def calcular_combustible(self):
        distancia = self.calcular_distancia()
        litros = distancia / self.rendimiento
        return litros

    def calcular_costo(self, precio_combustible):
        litros = self.calcular_combustible()
        costo_total = litros * precio_combustible
        return costo_total
    

    def main():
        rendimiento = float(input("Ingrese el rendimiento del vehículo (km/litro): "))
        origen = input("Ingrese la posición de origen (latitud:longitud): ")
        destino = input("Ingrese la posición de destino (latitud:longitud): ")
        precio_combustible = float(input("Ingrese el precio del combustible por litro: "))

        Transporte = Transporte(rendimiento, origen, destino)
        litros_necesarios = Transporte.calcular_combustible()
        costo_total = Transporte.calcular_costo(precio_combustible)

        print(f"Litros necesarios: {litros_necesarios:.2f} litros")
        print(f"Costo total de combustible: ${costo_total:.2f}")

if __name__ == "__main__":  Trasnporte.main()

