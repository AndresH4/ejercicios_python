print("Elegi un numero de 1 a 100, ¿Puedes adivinarlo?\n")
string_usuario=input("Ingresa l numero que estoy pensando")

numero_secreto = 50
intentos=int(string_usuario)

if intentos==numero_secreto:
    print("Lo encontraste")
else :
    print("Sigue intentando")