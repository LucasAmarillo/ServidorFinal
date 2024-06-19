import socket
import threading
import json
import sqlite3

class ServidorChat:
    def __init__(self, host='0.0.0.0', puerto=5000):
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((host, puerto))
        self.servidor.listen(5)
        self.clientes = []
        self.nombres_usuarios = {}
        print(f"Servidor funcionando en {host}:{puerto}")

    # Creacion de tabla usuarios

    def crear_tabla_usuarios(self):
        try:
            with sqlite3.connect('usuarios.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                nombre_usuario TEXT UNIQUE NOT NULL,
                                contrasena TEXT NOT NULL)''')
                conn.commit()
        except Exception as e:
            print(f"Error al crear la tabla 'usuarios': {e}")

    def autenticar_usuario(self, datos):
        conexion = sqlite3.connect('usuarios.db')
        cursor = conexion.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = ? AND contrasena = ?", (datos['nombre_usuario'], datos['contrasena']))
        usuario = cursor.fetchone()
        
        conexion.close()
        return usuario is not None

 
    def registrar(self,datos):
        conexion = sqlite3.connect('usuarios.db')
        cursor = conexion.cursor()
        
        cursor.execute("INSERT INTO usuarios (nombre_usuario,contrasena) values (?,?)", (datos['nombre_usuario'], datos['contrasena']))
        conexion.commit()
        
        conexion.close()
        return usuario is not None

    def manejar_cliente(self, socket_cliente):
        while True:
            try:
                mensaje = socket_cliente.recv(1024).decode('utf-8')
                if mensaje:
                    datos = json.loads(mensaje)
                    if datos['tipo'] == 'login':
                        if self.autenticar_usuario(datos):
                            socket_cliente.sendall(json.dumps({"tipo": "login", "estado": "exitoso"}).encode('utf-8'))
                            self.nombres_usuarios[socket_cliente] = datos['nombre_usuario']
                            self.clientes.append(socket_cliente)
                            self.enviar_usuarios_conectados()
                            threading.Thread(target=self.escuchar_mensajes, args=(socket_cliente,)).start()
                            return
                        else:
                            socket_cliente.sendall(json.dumps({"tipo": "login", "estado": "fallido"}).encode('utf-8'))
                            socket_cliente.close()
                            return
                    elif datos['tipo'] == 'registrar':
                        if self.registrar(datos):
                            socket_cliente.sendall(json.dumps({"tipo": "registro", "estado": "exitoso"}).encode('utf-8'))
                        else:
                            socket_cliente.sendall(json.dumps({"tipo": "registro", "estado": "fallido"}).encode('utf-8'))


            except:
                continue

    def escuchar_mensajes(self, socket_cliente):
        while True:
            try:
                mensaje = socket_cliente.recv(1024).decode('utf-8')
                if mensaje:
                    datos = json.loads(mensaje)
                    print(f"Recibido: {datos}")
                    if datos['tipo'] == 'desconectar':
                        self.eliminar(socket_cliente)
                        break
                    elif datos['tipo'] == 'privado':
                        self.enviar_mensaje_privado(datos)
                    else:
                        self.difundir(datos, socket_cliente)
                else:
                    self.eliminar(socket_cliente)
                    #break
            except:
                self.eliminar(socket_cliente)
                break

    def difundir(self, mensaje, socket_cliente):
        for cliente in self.clientes:
            if cliente != socket_cliente:
                try:
                    cliente.sendall(json.dumps(mensaje).encode('utf-8'))
                except:
                    self.eliminar(cliente)

    def enviar_mensaje_privado(self, datos):
        destino = datos['destino']
        for cliente, nombre_usuario in self.nombres_usuarios.items():
            if nombre_usuario == destino:
                try:
                    cliente.sendall(json.dumps(datos).encode('utf-8'))
                    # Enviar una copia del mensaje al remitente también
                    if cliente != datos['origen']:
                        datos['tipo'] = 'privado_remitente'
                        datos['destino'] = self.nombres_usuarios[datos['origen']]
                        self.nombres_usuarios[datos['origen']].sendall(json.dumps(datos).encode('utf-8'))
                except:
                    print("Error al enviar mensaje privado.")

    def eliminar(self, socket_cliente):
        if socket_cliente in self.clientes:
            self.clientes.remove(socket_cliente)
            if socket_cliente in self.nombres_usuarios:
                print(f"{self.nombres_usuarios[socket_cliente]} se ha desconectado.")
                del self.nombres_usuarios[socket_cliente]
                self.enviar_usuarios_conectados()  # Enviar la lista de usuarios actualizada

    def enviar_usuarios_conectados(self):
        usuarios = list(self.nombres_usuarios.values())
        mensaje = {
            "tipo": "usuarios",
            "usuarios": usuarios
        }
        for cliente in self.clientes:
            try:
                cliente.sendall(json.dumps(mensaje).encode('utf-8'))
            except:
                self.eliminar(cliente)

    def correr(self):
        while True:
            socket_cliente, direccion_cliente = self.servidor.accept()
            print(f"Conexión desde {direccion_cliente}")
            threading.Thread(target=self.manejar_cliente, args=(socket_cliente,)).start()

if __name__ == "__main__":
    servidor = ServidorChat()
    servidor.crear_tabla_usuarios()
    servidor.correr()
