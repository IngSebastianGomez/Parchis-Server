
import socket
import threading
import json
from queue import Queue
import tkinter as tk
from tkinter import messagebox
import random

# Variable para definir si se juega en local
local = True

# Cambio de IPs 
if local:
    # IP servidor publica
    IP_SERVER_PUBLICA = "localhost"
else:
    # IP servidor publica
    IP_SERVER_PUBLICA = "3.15.208.30"

# Puerto servidor
PORT_SERVER = 8001

cola_mensajes = Queue()
id_mensaje = 1

# Conectarse al servidor
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((IP_SERVER_PUBLICA, PORT_SERVER))

#Funcion para el hilo de cliente
def receive_messages():
    while True:
        try:
            mensaje = cliente.recv(1024).decode('utf-8')
            if mensaje:
                mensaje = json.loads(mensaje)
                cola_mensajes.put(mensaje)
        except:
            mostrar_respuesta("Desconectado del servidor")
            break

def manejar_mensajes():
    global id_mensaje
    while True:
        if not cola_mensajes.empty():
            # Procesar mensaje
            mensaje = cola_mensajes.get()
            if "id_broadcast" in mensaje:
                if mensaje['estado_partida'] != "lobby":
                    if mensaje['id_broadcast'] == id_mensaje:
                        # Ejecuto la accion del mensaje
                        id_mensaje += 1
                        procesar_mensaje(mensaje)
                    else:
                        # Devuelvo el mensaje a la cola
                        cola_mensajes.put(mensaje)
                else:
                    procesar_mensaje(mensaje)
            else:
                procesar_mensaje(mensaje)

def procesar_mensaje(mensaje):
    nuevo_mensaje = ""

    if "tipo" in mensaje:
        tipo = mensaje["tipo"]
        if tipo == "conexion":
            cliente = mensaje["cliente"]
            jugadores = mensaje["jugadores"]
            estado_partida = mensaje["estado_partida"]
            nuevo_mensaje = f"Se ha conectado el cliente {cliente}. Hay {jugadores} jugadores en la partida. Estado de la partida: {estado_partida}."
        elif tipo == "desconexion":
            cliente = mensaje["cliente"]
            jugadores = mensaje["jugadores"]
            estado_partida = mensaje["estado_partida"]
            nuevo_mensaje = f"Se ha desconectado el cliente {cliente}. Quedan {jugadores} jugadores en la partida. Estado de la partida: {estado_partida}."
        elif tipo == "finalizar":
            ganador = mensaje["ganador"]
            nuevo_mensaje = f"La partida ha finalizado. El ganador es {ganador}."
        elif tipo == "denegado":
            razon = mensaje["razon"]
            nuevo_mensaje = f"La solicitud ha sido denegada. Razón: {razon}."
        else:
            nuevo_mensaje = "Mensaje desconocido"
    else:
        if "turno_actual" in mensaje:
            turno_actual = mensaje["turno_actual"]
            solicitud_esperada = mensaje["solicitud_esperada"]
            estado_partida = mensaje["estado_partida"]
            ultimos_dados = mensaje["ultimos_dados"]
            ultima_ficha = mensaje["ultima_ficha"]
            ultimo_turno = mensaje["ultimo_turno"]
            jugadores = mensaje["jugadores"]
            
            nuevo_mensaje = f"Es el turno de {turno_actual}.\nSe espera una solicitud de {solicitud_esperada}.\nEl estado de la partida es {estado_partida}.\n"
            nuevo_mensaje += f"Últimos dados lanzados: D1={ultimos_dados['D1']}, D2={ultimos_dados['D2']}.\n"
            nuevo_mensaje += f"Última ficha movida: {ultima_ficha}.\n"
            nuevo_mensaje += f"Último turno jugado por {ultimo_turno}.\n"
            
            for jugador in jugadores:
                nombre = jugador["nombre"]
                color = jugador["color"]
                fichas = jugador["fichas"]
                contadores_fichas = jugador["contadores_fichas"]
                
                nuevo_mensaje += f"\nJugador: {nombre}\n"
                nuevo_mensaje += f"Color: {color}\n"
                nuevo_mensaje += "Fichas:\n"
                for ficha, estado in fichas.items():
                    nuevo_mensaje += f"- {ficha}: {estado}\n"
                nuevo_mensaje += "Contadores de fichas:\n"
                for ficha, contador in contadores_fichas.items():
                    nuevo_mensaje += f"- {ficha}: {contador}\n"
        elif "Blue" in mensaje:
            # {"Yellow": True , "Blue": True, "Green": True, "Red": True}
            blue = mensaje["Blue"]
            yellow = mensaje["Yellow"]
            green = mensaje["Green"]
            red = mensaje["Red"]
            nuevo_mensaje = f"Colores disponibles:\nBlue: {blue}\nYellow: {yellow}\nGreen: {green}\nRed: {red}\n"
        else:
            nuevo_mensaje = "Mensaje desconocido"
    mostrar_respuesta(nuevo_mensaje)

#Hilo para estar en constante funcionamiento
thread = threading.Thread(target=receive_messages)
thread2 = threading.Thread(target=manejar_mensajes)
thread.start()
thread2.start()

#Enviar solicitud de colores disponibles
def solicitud_color():
    solicitud = {"tipo": "solicitud_color"}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))
    messagebox.showinfo("Solicitud enviada", f"Solicitud: Solicitud color")

#Enviar solicitud de eleccion de color
def seleccion_color():
    def enviar_datos(nombre, color):
        # Enviar solicitud de seleccion de color
        solicitud = {"tipo": "seleccion_color", "nombre": nombre, "color": color}
        cliente.sendall(json.dumps(solicitud).encode('utf-8'))
        # Mostrar los valores en un mensaje de información
        messagebox.showinfo("Solicitud enviada", f"Solicitud: Seleccion color")

    def elegir_color(nombre):
        # Crear la ventana emergente
        ventana_emergente = tk.Tk()
        ventana_emergente.title("Elegir color")
        # Crear los botones de colores
        for color in ["Red", "Green", "Blue", "Yellow"]:
            boton = tk.Button(ventana_emergente, text=color, command=lambda: (enviar_datos(nombre, color), ventana_emergente.destroy()), padx=20)
            boton.pack(pady=5)

    # Crear la ventana emergente
    ventana_emergente = tk.Tk()
    ventana_emergente.title("Elegir nombre")
    ventana_emergente.geometry("200x100")
    # Crear las etiquetas de texto
    etiqueta_nombre = tk.Label(ventana_emergente, text="Nombre")
    etiqueta_nombre.pack()
    # Crear la casilla de texto para el nombre
    casilla_texto_nombre = tk.Entry(ventana_emergente)
    casilla_texto_nombre.pack()
    # Crear el botón de enviar
    boton_enviar = tk.Button(ventana_emergente, text="Enviar", command=lambda: (elegir_color(casilla_texto_nombre.get()), ventana_emergente.destroy()))
    boton_enviar.pack(pady=10)

#Enviar solicitud de iniciar la partida
def solicitud_iniciar_partida():
    solicitud = {"tipo": "solicitud_iniciar_partida"}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))
    messagebox.showinfo("Solicitud enviada", f"Solicitud: Iniciar partida")

#Enviar solicitud de lanzar los dados
def solicitud_lanzar_dados():
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    solicitud = {"tipo": "lanzar_dados", "dados": {"D1": d1, "D2": d2}}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))
    messagebox.showinfo("Solicitud enviada", f"Solicitud: Lanzar dados \n\nDados: {d1} y {d2}")

#Enviar solicitud de sacar ficha del tablero (ficha en estado de meta)
def solicitud_sacar_ficha():
    def enviar_datos(ficha):
        # Enviar solicitud de seleccion de color
        solicitud = {"tipo": "sacar_ficha", "ficha": ficha}
        cliente.sendall(json.dumps(solicitud).encode('utf-8'))
        # Mostrar los valores en un mensaje de información
        messagebox.showinfo("Solicitud enviada", f"Solicitud: Sacar ficha")
        # Cerrar la ventana emergente
        ventana_emergente.destroy()

    # Crear la ventana emergente
    ventana_emergente = tk.Tk()
    ventana_emergente.title("Elegir ficha")

    for i in range(1, 5):
        boton = tk.Button(ventana_emergente, text=f"F{i}", command=lambda i=i: enviar_datos(f"F{i}"), padx=20)
        boton.pack(pady=5)

#Enviar solicitud de sacar ficha de la carcel
def solicitud_sacar_carcel():
    solicitud = {"tipo": "sacar_carcel", "ficha": "F1"}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))
    messagebox.showinfo("Solicitud enviada", f"Solicitud: Sacar carcel")

#Enviar solicitud de mover ficha en el tablero
def solicitud_mover_ficha():
    def enviar_datos(ficha):
        # Enviar solicitud de seleccion de color
        solicitud = {"tipo": "mover_ficha", "ficha": ficha}
        cliente.sendall(json.dumps(solicitud).encode('utf-8'))
        # Mostrar los valores en un mensaje de información
        messagebox.showinfo("Solicitud enviada", f"Solicitud: Mover ficha")
        # Cerrar la ventana emergente
        ventana_emergente.destroy()

    # Crear la ventana emergente
    ventana_emergente = tk.Tk()
    ventana_emergente.title("Elegir ficha")

    for i in range(1, 5):
        boton = tk.Button(ventana_emergente, text=f"F{i}", command=lambda i=i: enviar_datos(f"F{i}"), padx=20)
        boton.pack(pady=5)

#Enviar solicitud de mover ficha en el tablero
def solicitud_bot():
    solicitud = {"tipo": "solicitud_bot"}
    cliente.sendall(json.dumps(solicitud).encode('utf-8'))
    messagebox.showinfo("Solicitud enviada", f"Solicitud: Activar bot")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Cliente de Parqués")

# Lista de solicitudes
solicitudes = {
    "Solicitud Color": solicitud_color,
    "Seleccion Color": seleccion_color,
    "Solicitud Iniciar Partida": solicitud_iniciar_partida,
    "Solicitud Lanzar Dados": solicitud_lanzar_dados,
    "Solicitud Sacar Ficha": solicitud_sacar_ficha,
    "Solicitud Sacar Carcel": solicitud_sacar_carcel,
    "Solicitud Mover Ficha": solicitud_mover_ficha,
    "Solicitud Bot": solicitud_bot,
}

# Crear botones de solicitudes
for i, solicitud in enumerate(solicitudes):
    boton = tk.Button(ventana, text=solicitud, command=lambda solicitud=solicitud: solicitudes[solicitud]())
    boton.grid(row=i, column=0, pady=5)

# Agregar área para mostrar la respuesta del servidor
respuesta_texto = tk.Text(ventana, width=40, height=25)
respuesta_texto.grid(row=len(solicitudes), column=0, pady=5)

# Agregar imagen del tablero
imagen_tablero = tk.PhotoImage(file="Tablero_right.png")
tablero_label = tk.Label(ventana, image=imagen_tablero)
tablero_label.grid(row=0, column=1, rowspan=len(solicitudes) + 1, padx=10)

# Función para mostrar la respuesta del servidor
def mostrar_respuesta(respuesta):
    respuesta_texto.delete(1.0, tk.END)
    respuesta_texto.insert(tk.END, respuesta)

# Ejecutar la ventana principal
ventana.mainloop()
