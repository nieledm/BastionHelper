import tkinter as tk
from tkinter import ttk, messagebox
import paramiko
from sshtunnel import SSHTunnelForwarder
import subprocess
import threading
import json
import sys
import os
import connections

# Função para carregar o arquivo de configuração JSON
def carregar_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            return config["BASTIONS"], config["SERVIDORES"]
    except Exception as e:
        messagebox.showerror("Erro ao carregar configurações", f"Erro ao carregar o arquivo config.json: {str(e)}")
        return {}, {}

# Função para salvar as configurações no arquivo JSON
def salvar_config(bastions_data, servidores_data):
    try:
        config = {
            "BASTIONS": bastions_data,
            "SERVIDORES": servidores_data
        }
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro ao salvar configurações", f"Erro ao salvar o arquivo config.json: {str(e)}")

# Carregar as configurações
BASTIONS, SERVIDORES = carregar_config()

def editar_config():
    def salvar():
        try:
            bastions_data = json.loads(bastions_text.get("1.0", tk.END))
            servidores_data = json.loads(servidores_text.get("1.0", tk.END))
            salvar_config(bastions_data, servidores_data)  # Salva as configurações no arquivo JSON
            edit_window.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao salvar", f"Erro ao salvar as configurações: {str(e)}")

    edit_window = tk.Toplevel()
    edit_window.title("Editar Configuração")
    edit_window.geometry("900x650")

    ttk.Label(edit_window, text="BASTIONS (JSON):").pack(anchor="w", pady=5)
    bastions_text = tk.Text(edit_window, height=15)
    bastions_text.pack(fill=tk.BOTH, expand=True, padx=10)
    bastions_text.insert("1.0", json.dumps(BASTIONS, indent=4))

    ttk.Label(edit_window, text="SERVIDORES (JSON):").pack(anchor="w", pady=5)
    servidores_text = tk.Text(edit_window, height=15)
    servidores_text.pack(fill=tk.BOTH, expand=True, padx=10)
    servidores_text.insert("1.0", json.dumps(SERVIDORES, indent=4))

    ttk.Button(edit_window, text="Salvar alterações", command=salvar).pack(pady=10)


def criar_interface():
    root = tk.Tk()
    root.title("Jump Helper")
    root.geometry("800x620")

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    config_menu = tk.Menu(menu_bar, tearoff=0)
    config_menu.add_command(label="Editar Servidores", command=editar_config)
    menu_bar.add_cascade(label="Configurações", menu=config_menu)

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Jump Helper", font=("Arial", 14, "bold")).pack(pady=(0, 20))

    servers_container = ttk.Frame(main_frame)
    servers_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    # =========================
    # 🔹 Bastion
    # =========================
    bastion_frame = ttk.LabelFrame(servers_container, text="Intermediário", padding="15")
    bastion_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    ttk.Label(bastion_frame, text="Selecione o servidor intermediário (bastion):").pack(anchor="w", pady=(5, 0))
    bastion_cb = ttk.Combobox(bastion_frame, values=list(BASTIONS.keys()))
    bastion_cb.pack(fill=tk.X, pady=(2, 10))

    ttk.Label(bastion_frame, text="Host:").pack(anchor="w")
    bastion_host = ttk.Entry(bastion_frame)
    bastion_host.pack(fill=tk.X, pady=2)

    ttk.Label(bastion_frame, text="Usuário:").pack(anchor="w")
    bastion_user = ttk.Entry(bastion_frame)
    bastion_user.pack(fill=tk.X, pady=2)

    ttk.Label(bastion_frame, text="Senha:").pack(anchor="w")
    bastion_pass = ttk.Entry(bastion_frame, show="*")
    bastion_pass.pack(fill=tk.X, pady=2)

    ttk.Label(bastion_frame, text="Porta:").pack(anchor="w")
    bastion_port = ttk.Entry(bastion_frame)
    bastion_port.pack(fill=tk.X, pady=2)

    def preencher_bastion(event):
        nome = bastion_cb.get()
        if nome in BASTIONS:
            b = BASTIONS[nome]
            bastion_host.delete(0, tk.END)
            bastion_user.delete(0, tk.END)
            bastion_pass.delete(0, tk.END)
            bastion_port.delete(0, tk.END)
            bastion_host.insert(0, b["host"])
            bastion_user.insert(0, b["user"])
            bastion_pass.insert(0, b["password"])
            bastion_port.insert(0, b["port"])

    bastion_cb.bind("<<ComboboxSelected>>", preencher_bastion)

    # =========================
    # 🔹 Servidor Final
    # =========================
    servidor_frame = ttk.LabelFrame(servers_container, text="Servidor Final", padding="15")
    servidor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    ttk.Label(servidor_frame, text="Selecione o Servidor:").pack(anchor="w", pady=(5, 0))
    servidor_cb = ttk.Combobox(servidor_frame, values=list(SERVIDORES.keys()))
    servidor_cb.pack(fill=tk.X, pady=(2, 10))

    ttk.Label(servidor_frame, text="Host:").pack(anchor="w")
    servidor_host = ttk.Entry(servidor_frame)
    servidor_host.pack(fill=tk.X, pady=2)

    ttk.Label(servidor_frame, text="Usuário:").pack(anchor="w")
    servidor_user = ttk.Entry(servidor_frame)
    servidor_user.pack(fill=tk.X, pady=2)

    ttk.Label(servidor_frame, text="Senha:").pack(anchor="w")
    servidor_pass = ttk.Entry(servidor_frame, show="*")
    servidor_pass.pack(fill=tk.X, pady=2)

    ttk.Label(servidor_frame, text="Porta:").pack(anchor="w")
    servidor_port = ttk.Entry(servidor_frame)
    servidor_port.pack(fill=tk.X, pady=2)

    def preencher_servidor(event):
        nome = servidor_cb.get()
        if nome in SERVIDORES:
            s = SERVIDORES[nome]
            servidor_host.delete(0, tk.END)
            servidor_user.delete(0, tk.END)
            servidor_pass.delete(0, tk.END)
            servidor_port.delete(0, tk.END)
            servidor_host.insert(0, s["host"])
            servidor_user.insert(0, s["user"])
            servidor_pass.insert(0, s["password"])
            servidor_port.insert(0, s["port"])

    servidor_cb.bind("<<ComboboxSelected>>", preencher_servidor)

    # =========================
    # 🔹 Rsync/Transferência
    # =========================
    rsync_frame = ttk.LabelFrame(main_frame, text="Rsync", padding="15")
    rsync_frame.pack(fill=tk.X, pady=10)

    ttk.Label(rsync_frame, text="Arquivo/Pasta de Origem (Local):").pack(anchor="w")
    rsync_origem = ttk.Entry(rsync_frame)
    rsync_origem.pack(fill=tk.X, pady=2)
    rsync_origem.insert(0, "/caminho/local/arquivo.txt") # Valor de exemplo

    ttk.Label(rsync_frame, text="Caminho de Destino (Remoto):").pack(anchor="w")
    rsync_destino = ttk.Entry(rsync_frame)
    rsync_destino.pack(fill=tk.X, pady=2)
    rsync_destino.insert(0, "/caminho/remoto/") # Valor de exemplo

    # =========================
    # 🔹 Botões
    # =========================
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)

    def on_conectar_ssh():
        b_nome = bastion_cb.get()
        s_nome = servidor_cb.get()

        if b_nome not in BASTIONS or s_nome not in SERVIDORES:
            messagebox.showerror("Erro", "Selecione bastion e servidor válidos.")
            return

        bastion_info = {
            "host": bastion_host.get(),
            "user": bastion_user.get(),
            "password": bastion_pass.get(),
            "port": bastion_port.get()
        }

        servidor_info = {
            "host": servidor_host.get(),
            "user": servidor_user.get(),
            "password": servidor_pass.get(),
            "port": servidor_port.get()
        }

        connections.conectar_ssh(bastion_info, servidor_info)

    def on_conectar_rdp():
        b_nome = bastion_cb.get()
        s_nome = servidor_cb.get()

        if b_nome not in BASTIONS or s_nome not in SERVIDORES:
            messagebox.showerror("Erro", "Selecione bastion e servidor válidos.")
            return

        bastion_info = {
            "host": bastion_host.get(),
            "user": bastion_user.get(),
            "password": bastion_pass.get(),
            "port": bastion_port.get()
        }

        servidor_info = {
            "host": servidor_host.get(),
            "user": servidor_user.get(),
            "password": servidor_pass.get(),
            "port": servidor_port.get()
        }

        connections.criar_tunel_rdp(bastion_info, servidor_info)
    

    def on_copiar_rsync():
        b_nome = bastion_cb.get()
        s_nome = servidor_cb.get()

        if b_nome not in BASTIONS or s_nome not in SERVIDORES:
            messagebox.showerror("Erro", "Selecione bastion e servidor válidos.")
            return

        # Pega as informações de login
        bastion_info = { 
            # ... (pegue os dados como você já faz para ssh/rdp)
            "host": bastion_host.get(),
            "user": bastion_user.get(),
            "password": bastion_pass.get(), # (Embora o rsync via ssh não use a senha do bastion no comando -J,
                                            # ele depende da autenticação ssh no terminal, que idealmente é por chave ou agent)
            "port": bastion_port.get()
        }
        servidor_info = { 
            # ... (pegue os dados do servidor final)
            "host": servidor_host.get(),
            "user": servidor_user.get(),
            "password": servidor_pass.get(), # (O rsync via ssh também pedirá a senha/chave do final)
            "port": servidor_port.get() # O rsync usa a porta 22 por padrão, mas você a tem aqui.
        }

        origem = rsync_origem.get()
        destino = rsync_destino.get()

        if not origem or not destino:
            messagebox.showerror("Erro", "Preencha a origem local e o destino remoto.")
            return

        connections.copiar_rsync(bastion_info, servidor_info, origem, destino)
    
    def on_criar_socks():
        b_nome = bastion_cb.get()

        if b_nome not in BASTIONS:
            messagebox.showerror("Erro", "Selecione um bastion válido.")
            return

        bastion_info = {
            "host": bastion_host.get(),
            "user": bastion_user.get(),
            "password": bastion_pass.get(), 
            "port": bastion_port.get()
        }

        # Você pode adicionar um campo para o usuário escolher a porta local aqui.
        # Por enquanto, usamos a porta padrão 8888
        connections.criar_tunel_socks(bastion_info, porta_local=8888)

    # Novo botão SOCKS
    ttk.Button(button_frame, text="SOCKS Proxy (-D)", command=on_criar_socks).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

    # Atualize a criação do button_frame:
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)

    # Botões existentes
    ttk.Button(button_frame, text="Conectar via SSH", command=on_conectar_ssh).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    ttk.Button(button_frame, text="Abrir RDP (via túnel)", command=on_conectar_rdp).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    # Novo botão Rsync
    ttk.Button(button_frame, text="Copiar via Rsync", command=on_copiar_rsync).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

    # ttk.Button(button_frame, text="Conectar via SSH", command=on_conectar_ssh).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    # ttk.Button(button_frame, text="Abrir RDP (via túnel)", command=on_conectar_rdp).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

    root.mainloop()

import gui

if __name__ == "__main__":
    gui.criar_interface()