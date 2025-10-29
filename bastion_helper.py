import tkinter as tk
from tkinter import ttk, messagebox
import paramiko
from sshtunnel import SSHTunnelForwarder
import subprocess
import threading
from config import SERVIDORES, BASTION_HOST, BASTION_USER, BASTION_PASS


def conectar_ssh(usuario_final, senha_final, servidor_final):
    try:
        bastion = paramiko.SSHClient()
        bastion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        bastion.connect(BASTION_HOST, username=BASTION_USER, password=BASTION_PASS)

        bastion_transport = bastion.get_transport()
        dest_addr = (servidor_final, 22)
        local_addr = ('127.0.0.1', 0)
        channel = bastion_transport.open_channel("direct-tcpip", dest_addr, local_addr)

        final = paramiko.SSHClient()
        final.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        final.connect(servidor_final, username=usuario_final, password=senha_final, sock=channel)

        stdin, stdout, stderr = final.exec_command("hostname && whoami")
        output = stdout.read().decode()
        messagebox.showinfo("Conectado!", f"Conexão OK!\n{output}")

        final.close()
        bastion.close()

    except Exception as e:
        messagebox.showerror("Erro", str(e))

def criar_tunel_rdp(usuario_final, senha_final, servidor_final, porta_local=3390):
    def iniciar_tunel():
        try:
            with SSHTunnelForwarder(
                (BASTION_HOST, 22),
                ssh_username=BASTION_USER,
                ssh_password=BASTION_PASS,
                remote_bind_address=(servidor_final, 3389),
                local_bind_address=('127.0.0.1', porta_local)
            ) as tunel:
                messagebox.showinfo("Túnel Ativo",
                    f"Túnel RDP ativo!\nConecte-se em: localhost:{porta_local}")
                subprocess.run(["mstsc", f"/v:localhost:{porta_local}"])
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    threading.Thread(target=iniciar_tunel).start()

def criar_interface():
    root = tk.Tk()
    root.title("Bastion Helper")

    ttk.Label(root, text="Servidor destino:").pack(pady=5)
    servidor_cb = ttk.Combobox(root, values=list(SERVIDORES.keys()))
    servidor_cb.pack(pady=5)

    ttk.Label(root, text="Usuário final:").pack(pady=5)
    usuario_entry = ttk.Entry(root)
    usuario_entry.pack(pady=5)

    ttk.Label(root, text="Senha final:").pack(pady=5)
    senha_entry = ttk.Entry(root, show="*")
    senha_entry.pack(pady=5)

    def on_conectar_ssh():
        nome = servidor_cb.get()
        if nome not in SERVIDORES:
            messagebox.showerror("Erro", "Selecione um servidor válido.")
            return
        conectar_ssh(usuario_entry.get(), senha_entry.get(), SERVIDORES[nome])

    def on_conectar_rdp():
        nome = servidor_cb.get()
        if nome not in SERVIDORES:
            messagebox.showerror("Erro", "Selecione um servidor válido.")
            return
        criar_tunel_rdp(usuario_entry.get(), senha_entry.get(), SERVIDORES[nome])

    ttk.Button(root, text="Conectar via SSH", command=on_conectar_ssh).pack(pady=10)
    ttk.Button(root, text="Abrir RDP (via túnel)", command=on_conectar_rdp).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    criar_interface()
