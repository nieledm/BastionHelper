from tkinter import messagebox
import paramiko
from sshtunnel import SSHTunnelForwarder
import subprocess
import threading
import sys

def interactive_shell(channel):
    import select

    def writeall():
        try:
            while True:
                data = sys.stdin.read(1)
                if not data:
                    break
                channel.send(data)
        except Exception:
            pass

    writer = threading.Thread(target=writeall)
    writer.daemon = True
    writer.start()

    while True:
        try:
            # Usa select para não travar leitura
            r, _, _ = select.select([channel], [], [], 0.1)
            if channel in r:
                data = channel.recv(1024)
                if not data:
                    break
                sys.stdout.write(data.decode(errors='ignore'))
                sys.stdout.flush()
            if channel.exit_status_ready() or channel.closed:
                break
        except Exception:
            break

def conectar_ssh(bastion_info, servidor_info):
    try:
        bastion = paramiko.SSHClient()
        bastion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        bastion.connect(
            bastion_info["host"],
            username=bastion_info["user"],
            password=bastion_info["password"],
            port=int(bastion_info["port"]),
            look_for_keys=False,
            allow_agent=False
        )

        bastion_transport = bastion.get_transport()
        dest_addr = (servidor_info["host"], int(servidor_info["port"]))
        local_addr = ('127.0.0.1', 0)
        channel = bastion_transport.open_channel("direct-tcpip", dest_addr, local_addr)

        final = paramiko.SSHClient()
        final.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        final.connect(
            servidor_info["host"],
            username=servidor_info["user"],
            password=servidor_info["password"],
            sock=channel,
            look_for_keys=False,
            allow_agent=False
        )

        transport = final.get_transport()
        session = transport.open_session()
        session.get_pty(term='xterm')
        session.invoke_shell()

        print("Conectado — shell interativo. Use Ctrl+D ou 'exit' para sair.")
        interactive_shell(session)  

        session.close()
        final.close()
        bastion.close()

    except Exception as e:
        messagebox.showerror("Erro de conexão", str(e))


def criar_tunel_rdp(bastion_info, servidor_info, porta_local=3390):
    def iniciar_tunel():
        try:
            with SSHTunnelForwarder(
                (bastion_info["host"], int(bastion_info["port"])),
                ssh_username=bastion_info["user"],
                ssh_password=bastion_info["password"],
                remote_bind_address=(servidor_info["host"], 3389),
                local_bind_address=('127.0.0.1', porta_local)
            ) as tunel:
                messagebox.showinfo(
                    "Túnel RDP",
                    f"Túnel ativo! Conecte-se via RDP em localhost:{porta_local}"
                )
                subprocess.run(["mstsc", f"/v:localhost:{porta_local}"])
        except Exception as e:
            messagebox.showerror("Erro no túnel", str(e))

    threading.Thread(target=iniciar_tunel).start()

def copiar_rsync(bastion_info, servidor_info, origem_local, destino_remoto):
    # Constrói o comando SSH Proxy/Jump
    # Você está usando a porta padrão 22 para o bastion, mas pode adaptar
    ssh_proxy_cmd = (
        f"ssh -J {bastion_info['user']}@{bastion_info['host']}:{bastion_info['port']}"
    )

    # Constrói o comando rsync
    rsync_cmd = [
        "rsync",
        "-av", # Arquivo, verbose, preserva permissões
        "-e", ssh_proxy_cmd,
        origem_local, # Arquivo ou diretório local
        f"{servidor_info['user']}@{servidor_info['host']}:{destino_remoto}" # Destino remoto
    ]

    def iniciar_rsync():
        try:
            messagebox.showinfo("Rsync", f"Iniciando cópia: {' '.join(rsync_cmd)}")
            # Executa o comando e espera a conclusão
            resultado = subprocess.run(rsync_cmd, check=True, capture_output=True, text=True)
            messagebox.showinfo("Rsync Concluído", f"Cópia finalizada com sucesso!\n\nSaída:\n{resultado.stdout}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro no Rsync", f"Falha na cópia:\n{e.stderr}")
        except FileNotFoundError:
             messagebox.showerror("Erro no Rsync", "O comando 'rsync' não foi encontrado. Verifique se está instalado e no PATH.")
        except Exception as e:
            messagebox.showerror("Erro no Rsync", str(e))

    # Executa em uma thread para não travar a GUI
    threading.Thread(target=iniciar_rsync).start()