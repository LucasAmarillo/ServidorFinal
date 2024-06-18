# import socket
# import threading
# import json
# import tkinter as tk
# from tkinter import simpledialog, messagebox, scrolledtext

# class ClienteChat:
#     def __init__(self, host='127.0.0.1', puerto=5000):
#         self.host = host
#         self.puerto = puerto
#         self.cliente = None
#         self.login_exitoso = False

#         self.ventana = tk.Tk()
#         self.ventana.title("Chat Cliente")

#         self.frame_login = tk.Frame(self.ventana)
#         self.label_usuario = tk.Label(self.frame_login, text="Usuario:")
#         self.label_usuario.pack(side=tk.LEFT)
#         self.entry_usuario = tk.Entry(self.frame_login)
#         self.entry_usuario.pack(side=tk.LEFT)
#         self.label_contrasena = tk.Label(self.frame_login, text="Contraseña:")
#         self.label_contrasena.pack(side=tk.LEFT)
#         self.entry_contrasena = tk.Entry(self.frame_login, show="*")
#         self.entry_contrasena.pack(side=tk.LEFT)
#         self.boton_login = tk.Button(self.frame_login, text="Login", command=self.enviar_credenciales)
#         self.boton_login.pack(side=tk.LEFT)
#         self.frame_login.pack()

#         self.frame_chat = tk.Frame(self.ventana)
#         self.chat_texto = scrolledtext.ScrolledText(self.frame_chat, state='disabled')
#         self.chat_texto.pack()

#         self.entry_mensaje = tk.Entry(self.frame_chat)
#         self.entry_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True)
#         self.boton_enviar = tk.Button(self.frame_chat, text="Enviar", command=self.enviar_mensaje)
#         self.boton_enviar.pack(side=tk.LEFT)

#         self.frame_chat.pack_forget()  # Esconde el frame del chat hasta que el login sea exitoso

#     def conectar(self):
#         if self.cliente:
#             self.cliente.close()
#         self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.cliente.connect((self.host, self.puerto))
#         threading.Thread(target=self.recibir_mensajes).start()

#     def enviar_credenciales(self):
#         self.conectar()  # Reconectar el socket
#         datos = {
#             "tipo": "login",
#             "nombre_usuario": self.entry_usuario.get(),
#             "contrasena": self.entry_contrasena.get()
#         }
#         self.cliente.send(json.dumps(datos).encode('utf-8'))

#     def recibir_mensajes(self):
#         while True:
#             try:
#                 mensaje = self.cliente.recv(1024).decode('utf-8')
#                 if mensaje:
#                     datos = json.loads(mensaje)
#                     if datos['tipo'] == 'login':
#                         if datos['estado'] == 'exitoso':
#                             self.login_exitoso = True
#                             self.frame_login.pack_forget()
#                             self.frame_chat.pack()
#                             self.chat_texto.config(state='normal')
#                             self.chat_texto.insert(tk.END, "Inicio de sesión exitoso.\n")
#                             self.chat_texto.config(state='disabled')
#                         else:
#                             messagebox.showerror("Error", "Inicio de sesión fallido. Credenciales incorrectas.")
#                             self.cliente.close()
#                             break
#                     elif datos['tipo'] == 'privado':
#                         self.chat_texto.config(state='normal')
#                         self.chat_texto.insert(tk.END, f"Privado de {datos['origen']}: {datos['mensaje']}\n")
#                         self.chat_texto.config(state='disabled')
#                     else:
#                         self.chat_texto.config(state='normal')
#                         self.chat_texto.insert(tk.END, f"{datos['origen']}: {datos['mensaje']}\n")
#                         self.chat_texto.config(state='disabled')
#             except Exception as e:
#                 self.chat_texto.config(state='normal')
#                 self.chat_texto.insert(tk.END, f"¡Ocurrió un error!: {e}\n")
#                 self.chat_texto.config(state='disabled')
#                 self.cliente.close()
#                 break

#     def enviar_mensaje(self):
#         if not self.login_exitoso:
#             messagebox.showwarning("Advertencia", "No se puede enviar el mensaje. Inicio de sesión no exitoso.")
#             return
        
#         mensaje = self.entry_mensaje.get()
#         if mensaje.startswith("/privado"):
#             try:
#                 _, destino, mensaje_privado = mensaje.split(" ", 2)
#                 datos = {
#                     "tipo": "privado",
#                     "origen": self.entry_usuario.get(),
#                     "destino": destino,
#                     "mensaje": mensaje_privado
#                 }
#             except ValueError:
#                 messagebox.showwarning("Advertencia", "Formato incorrecto. Usa: /privado usuario_destino mensaje")
#                 return
#         else:
#             datos = {
#                 "tipo": "difusion",
#                 "origen": self.entry_usuario.get(),
#                 "mensaje": mensaje
#             }
        
#         # Enviar el mensaje al servidor
#         self.cliente.send(json.dumps(datos).encode('utf-8'))

#         # Mostrar el mensaje en el chat local
#         self.chat_texto.config(state='normal')
#         self.chat_texto.insert(tk.END, f"Tú: {mensaje}\n")
#         self.chat_texto.config(state='disabled')
        
#         # Limpiar el campo de entrada de mensaje
#         self.entry_mensaje.delete(0, tk.END)

#     def desconectar(self):
#         if self.cliente:
#             datos = {
#                 "tipo": "desconectar",
#                 "origen": self.entry_usuario.get()
#             }
#             self.cliente.send(json.dumps(datos).encode('utf-8'))
#             self.cliente.close()
#         self.ventana.quit()

#     def iniciar(self):
#         self.ventana.protocol("WM_DELETE_WINDOW", self.desconectar)
#         self.ventana.mainloop()

# if __name__ == "__main__":
#     cliente = ClienteChat()
#     cliente.iniciar()
import socket
import threading
import json
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext

class ClienteChat:
    def __init__(self, host='127.0.0.1', puerto=5000):
        self.host = host
        self.puerto = puerto
        self.cliente = None
        self.login_exitoso = False

        self.ventana = tk.Tk()
        self.ventana.title("Chat Cliente")

        self.frame_login = tk.Frame(self.ventana)
        self.label_usuario = tk.Label(self.frame_login, text="Usuario:")
        self.label_usuario.pack(side=tk.LEFT)
        self.entry_usuario = tk.Entry(self.frame_login)
        self.entry_usuario.pack(side=tk.LEFT)
        self.label_contrasena = tk.Label(self.frame_login, text="Contraseña:")
        self.label_contrasena.pack(side=tk.LEFT)
        self.entry_contrasena = tk.Entry(self.frame_login, show="*")
        self.entry_contrasena.pack(side=tk.LEFT)
        self.boton_login = tk.Button(self.frame_login, text="Login", command=self.enviar_credenciales)
        self.boton_login.pack(side=tk.LEFT)
        self.frame_login.pack()

        self.frame_chat = tk.Frame(self.ventana)
        self.chat_texto = scrolledtext.ScrolledText(self.frame_chat, state='disabled')
        self.chat_texto.pack()

        self.entry_mensaje = tk.Entry(self.frame_chat)
        self.entry_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.boton_enviar = tk.Button(self.frame_chat, text="Enviar", command=self.enviar_mensaje)
        self.boton_enviar.pack(side=tk.LEFT)

        self.frame_chat.pack_forget()  # Esconde el frame del chat hasta que el login sea exitoso

    def conectar(self):
        if self.cliente:
            self.cliente.close()
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((self.host, self.puerto))
        threading.Thread(target=self.recibir_mensajes).start()

    def enviar_credenciales(self):
        self.conectar()  # Reconectar el socket
        datos = {
            "tipo": "login",
            "nombre_usuario": self.entry_usuario.get(),
            "contrasena": self.entry_contrasena.get()
        }
        self.cliente.sendall(json.dumps(datos).encode('utf-8'))

    def recibir_mensajes(self):
        while True:
            try:
                mensaje = self.cliente.recv(1024).decode('utf-8')
                if mensaje:
                    datos = json.loads(mensaje)
                    if datos['tipo'] == 'login':
                        if datos['estado'] == 'exitoso':
                            self.login_exitoso = True
                            self.frame_login.pack_forget()
                            self.frame_chat.pack()
                            self.chat_texto.config(state='normal')
                            self.chat_texto.insert(tk.END, "Inicio de sesión exitoso.\n")
                            self.chat_texto.config(state='disabled')
                        else:
                            messagebox.showerror("Error", "Inicio de sesión fallido. Credenciales incorrectas.")
                            self.cliente.close()
                            break
                    elif datos['tipo'] == 'privado':
                        self.chat_texto.config(state='normal')
                        self.chat_texto.insert(tk.END, f"Privado de {datos['origen']}: {datos['mensaje']}\n")
                        self.chat_texto.config(state='disabled')
                    else:
                        self.chat_texto.config(state='normal')
                        self.chat_texto.insert(tk.END, f"{datos['origen']}: {datos['mensaje']}\n")
                        self.chat_texto.config(state='disabled')
            except ConnectionError as e:
                print(f"Error de conexión: {e}")
                # self.eliminar(self.socket_cliente)
                break
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {e}")
                # self.eliminar(self.socket_cliente)
                break


    def enviar_mensaje(self):
        if not self.login_exitoso:
            messagebox.showwarning("Advertencia", "No se puede enviar el mensaje. Inicio de sesión no exitoso.")
            return
        
        mensaje = self.entry_mensaje.get()
        # if mensaje.startswith("/privado"):
        if mensaje.startswith("//"):
            try:
                _, destino, mensaje_privado = mensaje.split(" ", 2)
                datos = {
                    "tipo": "privado",
                    "origen": self.entry_usuario.get(),
                    "destino": destino,
                    "mensaje": mensaje_privado
                }
            except ValueError:
                messagebox.showwarning("Advertencia", "Formato incorrecto. Usa: /privado usuario_destino mensaje")
                return
        else:
            datos = {
                "tipo": "difusion",
                "origen": self.entry_usuario.get(),
                "mensaje": mensaje
            }
        
        # Enviar el mensaje al servidor
        self.cliente.sendall(json.dumps(datos).encode('utf-8'))

        # Mostrar el mensaje en el chat local
        self.chat_texto.config(state='normal')
        self.chat_texto.insert(tk.END, f"Tú: {mensaje}\n")
        self.chat_texto.config(state='disabled')
        
        # Limpiar el campo de entrada de mensaje
        self.entry_mensaje.delete(0, tk.END)

    def desconectar(self):
        if self.cliente:
            try:
                datos = {
                    "tipo": "desconectar",
                    "origen": self.entry_usuario.get()
                }
                self.cliente.sendall(json.dumps(datos).encode('utf-8'))
            except:
                pass
            self.cliente.close()
        self.ventana.quit()

    def iniciar(self):
        self.ventana.protocol("WM_DELETE_WINDOW", self.desconectar)
        self.ventana.mainloop()

if __name__ == "__main__":
    cliente = ClienteChat()
    cliente.iniciar()
