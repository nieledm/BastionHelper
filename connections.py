from tkinter import messagebox
import paramiko
from sshtunnel import SSHTunnelForwarder
import subprocess
import threading
import sys, os, json
import subprocess

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

# Importações necessárias no topo do arquivo (já devem existir)

def copiar_rsync(bastion_info, servidor_info, origem_local, destino_remoto):
    def iniciar_rsync():
        try:
            # Construir o comando SSH Proxy/Jump
            ssh_proxy_cmd = (
                f"ssh -J {bastion_info['user']}@{bastion_info['host']}:{bastion_info['port']}"
            )

            # Construir o comando rsync
            rsync_cmd = [
                "rsync",
                "-avh", # a=archive, v=verbose, h=human-readable
                "-e", ssh_proxy_cmd,
                origem_local, 
                f"{servidor_info['user']}@{servidor_info['host']}:{destino_remoto}" 
            ]

            messagebox.showinfo(
                "Rsync - Iniciando", 
                f"A cópia será iniciada em um terminal externo. Aguarde a conclusão.\n\nComando: {' '.join(rsync_cmd)}"
            )
            
            # Executa o comando em um novo terminal para que o usuário possa acompanhar o progresso
            if sys.platform.startswith('win'):
                # No Windows, usa 'start cmd /k' ou similar para abrir uma nova janela
                # No Linux/Mac, tenta usar 'xterm -e' ou 'gnome-terminal -e'   <-------------Preciso adaptar isso
                comando_completo = ["start", "cmd", "/k"] + rsync_cmd
            else:
                subprocess.run(rsync_cmd, check=True, text=True)
                messagebox.showinfo("Rsync Concluído", "Cópia finalizada com sucesso! Verifique o console para detalhes.")
                return

            # Executa a cópia
            subprocess.run(comando_completo, check=True)

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro no Rsync", f"Falha na cópia. Código de erro: {e.returncode}\n\n{e.stderr}")
        except FileNotFoundError:
             messagebox.showerror("Erro no Rsync", "O comando 'rsync' não foi encontrado. Verifique se está instalado e no PATH.")
        except Exception as e:
            messagebox.showerror("Erro no Rsync", str(e))

    # Executa em uma thread para não travar a GUI
    threading.Thread(target=iniciar_rsync).start()

def criar_tunel_socks(bastion_info, porta_local=8888):
    def iniciar_tunel_socks():
        try:
            # Se conecta apenas ao Bastion.
            with SSHTunnelForwarder(
                (bastion_info["host"], int(bastion_info["port"])),
                ssh_username=bastion_info["user"],
                ssh_password=bastion_info["password"],
            ) as tunel:
                socks_cmd = [
                    "ssh",
                    "-D", str(porta_local), # Porta local para o SOCKS
                    "-C", "-N", # Comprimir, e Não executar comando remoto
                    "-J", f"{bastion_info['user']}@{bastion_info['host']}:{bastion_info['port']}",
                    f"{bastion_info['user']}@{bastion_info['host']}" # Conexão SOCKS ao Bastion
                ]
                
                messagebox.showinfo(
                    "Túnel SOCKS",
                    f"Túnel SOCKS ativo na porta: localhost:{porta_local}\n\n"
                    "Configure seu navegador/aplicação para usar este SOCKS Proxy (v5)."
                )
                
                # Executa o comando e mantém a conexão aberta no console
                subprocess.run(socks_cmd, check=True) # Isso vai bloquear até ser fechado (Ctrl+C)

        except Exception as e:
            messagebox.showerror("Erro no Túnel SOCKS", str(e))

    threading.Thread(target=iniciar_tunel_socks).start()