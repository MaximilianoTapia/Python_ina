personas=[["juan",20,"bravo de s"],"maria","pedro","macarena"]
personas.append("cristina")
personas.pop()
#print(personas)
p = {
    "nombre":"juan",
    "apellido":"perez",
    "edad":20,
    "estatura": 1.60,
    "hobby":["Futbol","Tenis","Payaya"],
    "padres":{"madre":"juana","padre":"Luis"}
    }
p["edad"]=25 #modificación directa
p.update({"estatura":1.70,"nombre":"JUAN"}) #actualizo varias llaves
del p["nombre"] #Elimino un una llave
print(p.get("nombre")) #Obtener una llave
print(p["edad"])
print(p["padres"]["madre"])
p["fec_nac"]="10/10/2010"
p["padres"]["hno"]="Elias"
print(p)
for k1 in p.keys():
    print(k1)
for v in p.values():
    print(v)
for k,v in p.items():
    print(f"{k} su valor es: {v}")