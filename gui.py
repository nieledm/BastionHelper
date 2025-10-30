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
from config import SERVIDORES, BASTIONS

def editar_config():
    def salvar():
        try:
            bastions_data = json.loads(bastions_text.get("1.0", tk.END))
            servidores_data = json.loads(servidores_text.get("1.0", tk.END))
            with open("config.py", "w", encoding="utf-8") as f:
                f.write("# Arquivo gerado automaticamente pelo Jump Helper\n\n")
                f.write(f"BASTIONS = {json.dumps(bastions_data, indent=4)}\n\n")
                f.write(f"SERVIDORES = {json.dumps(servidores_data, indent=4)}\n")
            messagebox.showinfo("Sucesso", "Arquivo atualizado com sucesso!\n\nReinicie o programa para aplicar as mudanças.")
            edit_window.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao salvar", str(e))

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
    root.geometry("750x500")

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

    ttk.Label(bastion_frame, text="Selecione o servidor intermediário (Bastion):").pack(anchor="w", pady=(5, 0))
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

    ttk.Button(button_frame, text="Conectar via SSH", command=on_conectar_ssh).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    ttk.Button(button_frame, text="Abrir RDP (via túnel)", command=on_conectar_rdp).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

    root.mainloop()
