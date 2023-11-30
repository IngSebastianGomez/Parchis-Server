import socket
import threading
import json
from queue import Queue
import random
import colorama
from colorama import Fore,Style,Back,init
init(autoreset=True)

# Variable para definir si se juega en local
local = True

# Cambio de IPs 
if local:
    # IP servidor publica
    IP_SERVER_PUBLICA = "localhost"
else:
    # IP servidor publica
    IP_SERVER_PUBLICA = "192.168.20.12"

# Puerto servidor
PORT_SERVER = 8001

# Conectarse al servidor
try:
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((IP_SERVER_PUBLICA, PORT_SERVER))
except:
    print("Error: No se pudo conectar con el servidor.")
    exit()

QueueMessage = Queue()
IDmessage = 1

#Funcion para el hilo de cliente
def GetMessage():
    while True:
        try:
            mensaje = cliente.recv(1024).decode('utf-8')
            if mensaje:
                mensaje = json.loads(mensaje)
                QueueMessage.put(mensaje)
        except:
            print("Desconectado del servidor")
            break

def HandleMessage():
    global IDmessage
    while True:
        if not QueueMessage.empty():
            # Procesar mensaje
            mensaje = QueueMessage.get()
            if "id_broadcast" in mensaje:
                if mensaje['estado_partida'] != "lobby":
                    if mensaje['id_broadcast'] == IDmessage:
                        # Ejecuto la accion del mensaje
                        IDmessage += 1
                        ProcessMessage(mensaje)
                    else:
                        # Devuelvo el mensaje a la cola
                        QueueMessage.put(mensaje)
                else:
                    ProcessMessage(mensaje)
            else:
                ProcessMessage(mensaje)

def ProcessMessage(mensaje):
    nuevo_mensaje = ""

    if "tipo" in mensaje:
        tipo = mensaje["tipo"]
        if tipo == "conexion":
            cliente = mensaje["cliente"]
            informacion = f"Se ha conectado el cliente {cliente}.\n"
            print("\nMensaje recibido:\n" + informacion)
        elif tipo == "desconexion":
            cliente = mensaje["cliente"]
            jugadores = mensaje["jugadores"]
            informacion = f"Se ha desconectado el cliente {cliente}.\nQuedan {jugadores} jugadores en la partida.\n"
            print("\nMensaje recibido:\n" + informacion)
        elif tipo == "finalizar":
            ganador = mensaje["ganador"]
            informacion = f"La partida ha finalizado.\nEl ganador es {ganador}.\n"
            print("\nMensaje recibido:\n" + informacion)
        elif tipo == "denegado":
            razon = mensaje["razon"]
            informacion = f"La solicitud ha sido denegada.\nRazón: {razon}.\n"
            print("\nMensaje recibido:\n" + informacion)
        else:
            informacion = "Mensaje desconocido\n"
            print("\nMensaje recibido:\n" + informacion)
    else:
        if "turno_actual" in mensaje:
            turno_actual = mensaje["turno_actual"]
            solicitud_esperada = mensaje["solicitud_esperada"]
            estado_partida = mensaje["estado_partida"]
            ultimos_dados = mensaje["ultimos_dados"]
            ultimo_turno = mensaje["ultimo_turno"]
            jugadores = mensaje["jugadores"]
            # Mapear colores según el nombre del jugador
            colores = {"Red": Fore.RED, "Yellow": Fore.YELLOW, "Blue": Fore.BLUE, "Green": Fore.GREEN}
            # Crear mensaje
            nuevo_mensaje = f"El estado de la partida es {estado_partida}.\n"
            
            # Mostrar jugadores
            for jugador in jugadores:
                nombre = jugador["nombre"]
                color = jugador["color"]

                # Obtener el color asociado al jugador actual
                color_jugador = colores.get(color, Fore.WHITE)  # Por defecto, blanco si no hay coincidencia

                nuevo_mensaje += f"\nJugador: {color_jugador}{nombre}{Style.RESET_ALL}\n"
                nuevo_mensaje += f"Color: {color_jugador}{color}{Style.RESET_ALL}\n"

                # Mostrar fichas y contadores de fichas
                nuevo_mensaje += "Fichas y Count:\n"
                for ficha, estado in jugador["fichas"].items():
                    contador = jugador["contadores_fichas"].get(ficha, "N/A")
                    nuevo_mensaje += f"  {color_jugador}{ficha}: {estado} | Count: {contador} {Style.RESET_ALL}\n"


            # Mostrar mensaje
            if ultimos_dados['D1'] != 0 and ultimos_dados['D2'] != 0:
                #get name of last player
                if ultimo_turno == "Red":
                    GetColorUltimo_turno = Fore.RED
                elif ultimo_turno == "Yellow":
                    GetColorUltimo_turno = Fore.YELLOW
                elif ultimo_turno == "Blue":
                    GetColorUltimo_turno = Fore.BLUE
                elif ultimo_turno == "Green":
                    GetColorUltimo_turno = Fore.GREEN

                nuevo_mensaje += f"\n{GetColorUltimo_turno}Ultimo turno: , {ultimo_turno} {Style.RESET_ALL}"
                nuevo_mensaje += f"\nÚltimos dados lanzados: D1={ultimos_dados['D1']}, D2={ultimos_dados['D2']}.\n"

                if ultimos_dados['D1'] == ultimos_dados['D2']:
                    nuevo_mensaje += f"{Fore.MAGENTA}¡Dobles! {turno_actual} puede lanzar otra vez.{Fore.RESET}\n"

            if turno_actual != "":
                # Obtener el color asociado al jugador actual
                color_turno = colores.get(turno_actual, Fore.WHITE)  # Por defecto, blanco si no hay coincidencia
                nuevo_mensaje += f"Turno de {color_turno}{turno_actual}{Style.RESET_ALL}.\n"

            if solicitud_esperada != "":
                color_turno = colores.get(solicitud_esperada, Fore.WHITE)  # Por defecto, blanco si no hay coincidencia
                if solicitud_esperada == "lanzar_dados":
                    nuevo_mensaje += f"{color_turno}Puedes lanzar dados. Presiona 3 para lanzarlos.{Style.RESET_ALL}\n"
                elif solicitud_esperada == "mover_ficha":
                    nuevo_mensaje += f"{color_turno}Puedes mover la ficha. Presiona 4 para moverla.{Style.RESET_ALL}\n"
                elif solicitud_esperada == "sacar_carcel":
                    nuevo_mensaje += f"{color_turno}Puedes sacar ficha de la cárcel. Presiona 5 para sacar ficha de la cárcel.{Style.RESET_ALL}\n"
                elif solicitud_esperada == "sacar_ficha":
                    nuevo_mensaje += f"{color_turno}Puedes sacar una ficha del tablero. Presiona 6 para sacarla del tablero.{Style.RESET_ALL}\n"
                else:
                    nuevo_mensaje += f"Se espera la solicitud {solicitud_esperada}.\n"


            
            
            print("\nMensaje recibido:\n" + nuevo_mensaje)
        elif "Blue" in mensaje:
            blue = mensaje["Blue"]
            yellow = mensaje["Yellow"]
            green = mensaje["Green"]
            red = mensaje["Red"]
            informacion = (
                f"Colores disponibles:\n"
                f"{Fore.BLUE}Blue: {blue}\n"
                f"{Fore.YELLOW}Yellow: {yellow}\n"
                f"{Fore.GREEN}Green: {green}\n"
                f"{Fore.RED}Red: {red}\n"
                f"{Style.RESET_ALL}"  # Restablece el color al valor predeterminado
    )
            print("\nMensaje recibido:\n" + informacion)
        else:
            informacion = "Mensaje desconocido"
            print("\nMensaje recibido:\n" + informacion)

#Hilo para estar en constante funcionamiento
thread = threading.Thread(target=GetMessage)
thread2 = threading.Thread(target=HandleMessage)
thread.start()
thread2.start()

#Enviar solicitud de colores disponibles
def solicitud_color():
    solicitud = {"tipo": "solicitud_color"}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))
    input("Presiona Enter para continuar...")
    
    
#Enviar solicitud de eleccion de color
def seleccion_color():
    nombre = input("Ingrese nombre: ")
    color = input("Ingrese color: ")
    solicitud = {"tipo": "seleccion_color", "nombre": nombre, "color": color}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))

#Enviar solicitud de iniciar la partida
def RequestStartGame():
    solicitud = {"tipo": "solicitud_iniciar_partida"}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))

#Enviar solicitud de lanzar los dados
def RequestLaunchDados():
    d1 = random.randint(1,6)
    d2 = random.randint(1,6)
    solicitud = {"tipo": "lanzar_dados", "dados": {"D1": d1, "D2": d2}}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))

#Enviar solicitud de sacar ficha del tablero (ficha en estado de meta)
def RequestTokenToGoal():
    ficha = input("Ingrese ficha a sacar del tablero: ")
    solicitud = {"tipo": "sacar_ficha", "ficha": ficha}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))

#Enviar solicitud de sacar ficha de la carcel
def RequestGetOutOfJail():
    ficha = input("Ingrese ficha a sacar de la carcel: ")
    solicitud = {"tipo": "sacar_carcel", "ficha": ficha}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))

#Enviar solicitud de mover ficha en el tablero
def RequestMoveToken():
    ficha = input("Ingrese ficha a mover en el tablero: ")
    solicitud = {"tipo": "mover_ficha", "ficha": ficha}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))

#Enviar solicitud de mover ficha en el tablero
def RequestAddBot():
    solicitud = {"tipo": "solicitud_bot"}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))

def ShowInitialMenu():
    print("Bienvenido al juego. Colores disponibles:")
    solicitud_color()
    input("Presiona Enter para continuar...")
    print("\nIngrese su nombre y seleccione un color:")
    seleccion_color()

def mostrar_menu_OpcLobby():
    print(Fore.GREEN + "\nMenú de OpcLobby:")
    print("1. Iniciar partida")
    print("2. Incluir un Bot")
    print("3. Lanzar dados")
    print("4. Mover ficha en el tablero")
    print("5. Sacar ficha de la cárcel")
    print("6. acar ficha del tablero")
    print("0. Salir del juego")
    print("\nIngrese una opción... ")

def altMenu ():
    print(Back.MAGENTA +"3. Lanzar dados, 4. Sacar ficha, 5. Sacar cárcel, 6. Mover ficha, 0. Salir del juego")

OpcLobby = {
    1: RequestStartGame,
    2: RequestAddBot,
    3: RequestLaunchDados,
    4: RequestMoveToken,
    5: RequestGetOutOfJail,
    6: RequestTokenToGoal,
}

OpcGame = {
    3: RequestLaunchDados,
    4: RequestMoveToken,
    5: RequestGetOutOfJail,
    6: RequestTokenToGoal,
}

# Mostrar colores disponibles y solicitar nombre y color
ShowInitialMenu()

while True:
    try:
        
        solicitud = int(input())
        
        if solicitud == 0:
            print("Saliendo del juego. ¡Hasta luego!")
            break
        
        if solicitud in OpcLobby:
            OpcLobby[solicitud]()
        else:
            print(Back.RED + "Error: Opción no válida." + Back.RESET)
    except ValueError:
        print(Back.RED + "Error: Debes ingresar un número válido." + Back.RESET)
