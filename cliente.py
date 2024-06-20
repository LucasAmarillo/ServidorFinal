import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk

class ClienteChat:
    def __init__(self, host='127.0.0.1', puerto=5000):
        self.host = host
        self.puerto = puerto
        self.cliente = None
        self.login_exitoso = False

        self.ventana = tk.Tk()
        self.ventana.title("Chat Cliente")
        self.ventana.iconbitmap("logo.ico")
        self.ventana.resizable(False, False)
        ancho = 900
        alto = 600
        x = self.ventana.winfo_screenwidth() // 2 - ancho // 2
        y = self.ventana.winfo_screenheight() // 2 - alto // 2
        self.ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        self.frame_login = tk.Frame(self.ventana)

        imagen = Image.open("logo.png")
        self.logo_portada = ImageTk.PhotoImage(imagen)
        self.lblImagen = tk.Label(self.frame_login, image=self.logo_portada)
        self.lblImagen.pack(pady=50)

        self.label_usuario = tk.Label(self.frame_login, text="Usuario:")
        self.label_usuario.pack()
        self.entry_usuario = tk.Entry(self.frame_login, width=30)
        self.entry_usuario.focus_set()
        self.entry_usuario.pack()
        self.label_contrasena = tk.Label(self.frame_login, text="Contraseña:")
        self.label_contrasena.pack()
        self.entry_contrasena = tk.Entry(self.frame_login, width=30, show="*")
        self.entry_contrasena.pack()
        self.boton_login = tk.Button(self.frame_login, text="Ingresar", width=20, height=2, command=self.enviar_credenciales)
        self.boton_login.pack(pady=10)
        self.entry_contrasena.bind("<Return>", lambda event: self.enviar_credenciales())
        # Botón para registrar usuario
        self.boton_register = tk.Button(self.frame_login, text="Registrar", width=20, height=2, command=self.registrar)
        self.boton_register.pack(pady=10)
        self.frame_login.pack()

        self.frame_chat = tk.Frame(self.ventana)
        self.chat_texto = scrolledtext.ScrolledText(self.frame_chat, state='disabled')
        self.chat_texto.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.frame_mensaje = tk.Frame(self.frame_chat)
        self.entry_mensaje = tk.Entry(self.frame_mensaje)
        self.entry_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.boton_enviar = tk.Button(self.frame_mensaje, text="Enviar", command=self.enviar_mensaje)
        self.boton_enviar.pack(side=tk.LEFT)
        self.frame_mensaje.pack(side=tk.BOTTOM, fill=tk.X)

        self.frame_usuarios = tk.Frame(self.ventana, pady=10, padx=10)
        self.lista_usuarios = tk.Listbox(self.frame_usuarios)
        self.lista_usuarios.pack(fill=tk.BOTH, expand=True)
        self.label_usuarios = tk.Label(self.frame_usuarios, text=f"Usuarios Conectados:")
        self.label_usuarios.pack()
        self.label_cantidad_usuarios = tk.Label(self.frame_usuarios, text="")
        self.label_cantidad_usuarios.pack()

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
            "nombre_usuario": self.entry_usuario.get().lower(),
            "contrasena": self.entry_contrasena.get()
        }
        self.cliente.sendall(json.dumps(datos).encode('utf-8'))
    
    def registrar(self):
        self.conectar()  # Reconectar el socket
        datos = {
            "tipo": "registrar",
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
                    print(f"Recibido: {datos}")
                    if datos['tipo'] == 'login':
                        if datos['estado'] == 'exitoso':
                            self.ventana.title(f"Chat Cliente - Iniciado como {datos['nombre']}")
                            self.login_exitoso = True
                            self.entry_mensaje.focus_set()
                            self.entry_mensaje.bind("<Return>", lambda event: self.enviar_mensaje())
                            self.frame_login.pack_forget()
                            self.frame_chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                            self.chat_texto.config(state='normal')
                            self.chat_texto.insert(tk.END, "Inicio de sesión exitoso.\n")
                            self.chat_texto.config(state='disabled')
                            self.frame_usuarios.pack(side=tk.RIGHT, fill=tk.Y)
                        else:
                            messagebox.showerror("Error", "Inicio de sesión fallido. Credenciales incorrectas.")
                            self.cliente.close()
                            break
                    elif datos['tipo'] == 'usuarios':
                        self.actualizar_lista_usuarios(datos['usuarios'])
                        self.label_usuarios.config(text=f"Usuarios Conectados: {datos['cantidad']}")
                        
                    elif datos['tipo'] == 'privado':
                        self.chat_texto.config(state='normal')
                        self.chat_texto.insert(tk.END, f"Privado de {datos['origen']}: {datos['mensaje']}\n", 'rojo')
                        self.chat_texto.tag_config('rojo', foreground='red')
                        self.chat_texto.config(state='disabled')
                    else:
                        self.chat_texto.config(state='normal')
                        self.chat_texto.insert(tk.END, f"{datos['origen']}: {datos['mensaje']}\n")
                        self.chat_texto.config(state='disabled')

            except ConnectionError as e:
                print(f"Error de conexión: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {e}")
                break

    def enviar_mensaje(self):
        if not self.login_exitoso:
            messagebox.showwarning("Advertencia", "No se puede enviar el mensaje. Inicio de sesión no exitoso.")
            return

        mensaje = self.entry_mensaje.get()
        if mensaje.startswith("@"):
            try:
                destino, mensaje_privado = mensaje[1:].split(" ", 1)
                datos = {
                    "tipo": "privado",
                    "origen": self.entry_usuario.get(),
                    "destino": destino,
                    "mensaje": mensaje_privado
                }

                # Mostrar el mensaje en el chat local sin el destinatario
                self.chat_texto.config(state='normal')
                self.chat_texto.insert(tk.END, f"Tú (privado): {mensaje_privado}\n", 'rojo')
                self.chat_texto.tag_config('rojo', foreground='red')
                self.chat_texto.config(state='disabled')
            except ValueError:
                messagebox.showwarning("Advertencia", "Formato incorrecto. Usa: @usuario_destino mensaje")
                return
        else:
            datos = {
                "tipo": "difusion",
                "origen": self.entry_usuario.get(),
                "mensaje": mensaje
            }

            # Mostrar el mensaje en el chat local
            self.chat_texto.config(state='normal')
            self.chat_texto.insert(tk.END, f"Tú: {mensaje}\n", 'negro')
            self.chat_texto.tag_config('negro', foreground='black')
            self.chat_texto.config(state='disabled')

        # Enviar el mensaje al servidor
        self.cliente.sendall(json.dumps(datos).encode('utf-8'))

        # Limpiar el campo de entrada de mensaje
        self.entry_mensaje.delete(0, tk.END)

    def actualizar_lista_usuarios(self, usuarios):
        self.lista_usuarios.delete(0, tk.END)
        for usuario in usuarios:
            self.lista_usuarios.insert(tk.END, usuario)

        # # Actualizar la etiqueta de cantidad de usuarios
        # self.label_cantidad_usuarios.config(text=f"Usuarios Conectados: {datos['cantidad']}")

    def iniciar(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    cliente = ClienteChat()
    cliente.iniciar()
