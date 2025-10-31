"""
Janela principal da aplicação
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from config.manager import ConfigManager
from gui.components import ServerFormFrame, ConfigEditor, StatusBar
from gui.styles import setup_styles, COLORS
import connections

class MainWindow:
    """Janela principal da aplicação"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.bastions, self.servidores = ConfigManager.carregar_config()
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        
    def setup_window(self):
        """Configura a janela principal"""
        self.root.title("Jump Helper - Gerenciador de Conexões SSH")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Centralizar na tela
        self.root.eval('tk::PlaceWindow . center')
        
    def setup_styles(self):
        """Configura os estilos"""
        self.style = setup_styles()
        
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        self.create_header(main_frame)
        
        # Menu
        self.create_menu()
        
        # Container dos servidores
        self.create_servers_section(main_frame)
        
        # Seção Rsync
        self.create_rsync_section(main_frame)
        
        # Botões de ação
        self.create_action_buttons(main_frame)
        
        # Barra de status
        self.create_status_bar()
    
    def create_header(self, parent):
        """Cria o cabeçalho"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Jump Helper", 
                 font=("Arial", 18, "bold"), 
                 foreground=COLORS['primary']).pack(side=tk.LEFT)
    
    def create_menu(self):
        """Cria a barra de menu"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # Menu Configurações
        config_menu = tk.Menu(menu_bar, tearoff=0)
        config_menu.add_command(label="Editar Configurações", command=self.editar_config)
        config_menu.add_separator()
        config_menu.add_command(label="Recarregar Configurações", command=self.recarregar_config)
        menu_bar.add_cascade(label="Configurações", menu=config_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.mostrar_sobre)
        menu_bar.add_cascade(label="Ajuda", menu=help_menu)
    
    def create_servers_section(self, parent):
        """Cria a seção de servidores"""
        servers_container = ttk.Frame(parent)
        servers_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Frame do Bastion
        self.bastion_frame = ServerFormFrame(
            servers_container, "Servidor Intermediário (Bastion)", self.bastions
        )
        self.bastion_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Frame do Servidor Final
        self.servidor_frame = ServerFormFrame(
            servers_container, "Servidor Final", self.servidores
        )
        self.servidor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    def create_rsync_section(self, parent):
        """Cria a seção de transferência de arquivos"""
        rsync_frame = ttk.LabelFrame(parent, text="Transferência de Arquivos (Rsync)", padding="15")
        rsync_frame.pack(fill=tk.X, pady=10)
        
        # Origem
        ttk.Label(rsync_frame, text="Origem (Local):").pack(anchor="w")
        self.rsync_origem = ttk.Entry(rsync_frame)
        self.rsync_origem.pack(fill=tk.X, pady=(2, 10))
        self.rsync_origem.insert(0, "/caminho/local/arquivo.txt")
        
        # Destino
        ttk.Label(rsync_frame, text="Destino (Remoto):").pack(anchor="w")
        self.rsync_destino = ttk.Entry(rsync_frame)
        self.rsync_destino.pack(fill=tk.X, pady=(2, 10))
        self.rsync_destino.insert(0, "/caminho/remoto/")
        
        # Botões de ação do rsync
        rsync_buttons = ttk.Frame(rsync_frame)
        rsync_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(rsync_buttons, text="Upload →", 
                  command=self.on_upload_rsync).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rsync_buttons, text="Download ←", 
                  command=self.on_download_rsync).pack(side=tk.LEFT)
        
        ttk.Button(rsync_buttons, text="Procurar...", 
                  command=self.procurar_arquivo).pack(side=tk.RIGHT)
    
    def create_action_buttons(self, parent):
        """Cria os botões de ação principais"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Botões principais
        buttons_config = [
            ("🌐 Conectar SSH", self.on_conectar_ssh, COLORS['success']),
            ("🖥️ Abrir RDP", self.on_conectar_rdp, COLORS['accent']),
            ("🔒 SOCKS Proxy", self.on_criar_socks, COLORS['warning']),
            ("🔄 Copiar Rsync", self.on_upload_rsync, COLORS['primary'])
        ]
        
        for text, command, color in buttons_config:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    def create_status_bar(self):
        """Cria a barra de status"""
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message):
        """Atualiza a barra de status"""
        self.status_bar.update_status(message)
    
    def editar_config(self):
        """Abre o editor de configurações"""
        ConfigEditor(self.root, self.bastions, self.servidores, self.on_config_saved)
    
    def on_config_saved(self, new_bastions, new_servidores):
        """Callback quando as configurações são salvas"""
        self.bastions = new_bastions
        self.servidores = new_servidores
        self.recarregar_comboboxes()
    
    def recarregar_comboboxes(self):
        """Recarrega os valores dos comboboxes"""
        self.bastion_frame.combobox['values'] = list(self.bastions.keys())
        self.servidor_frame.combobox['values'] = list(self.servidores.keys())
    
    def recarregar_config(self):
        """Recarrega as configurações do arquivo"""
        self.bastions, self.servidores = ConfigManager.carregar_config()
        self.recarregar_comboboxes()
        messagebox.showinfo("Sucesso", "Configurações recarregadas!")
    
    def mostrar_sobre(self):
        """Mostra informações sobre o aplicativo"""
        about_text = """
Jump Helper - Gerenciador de Conexões SSH

Uma interface moderna para gerenciar conexões SSH
através de servidores bastion.

Funcionalidades:
• Conexão SSH através de bastion
• Túnel RDP para servidores Windows
• Proxy SOCKS para navegação segura
• Transferência de arquivos via Rsync

Desenvolvido para facilitar o acesso remoto a servidores.
"""
        messagebox.showinfo("Sobre", about_text)
    
    def validar_servidores(self):
        """Valida se os servidores estão selecionados"""
        bastion_nome = self.bastion_frame.get_selected_server()
        servidor_nome = self.servidor_frame.get_selected_server()
        
        if not bastion_nome or bastion_nome not in self.bastions:
            messagebox.showerror("Erro", "Selecione um bastion válido.")
            return False
        
        if not servidor_nome or servidor_nome not in self.servidores:
            messagebox.showerror("Erro", "Selecione um servidor válido.")
            return False
        
        return True
    
    # Handlers de eventos
    def on_conectar_ssh(self):
        if not self.validar_servidores():
            return
        
        bastion_info = self.bastion_frame.get_data()
        servidor_info = self.servidor_frame.get_data()
        
        self.update_status("Conectando via SSH...")
        threading.Thread(
            target=connections.conectar_ssh, 
            args=(bastion_info, servidor_info),
            daemon=True
        ).start()
    
    def on_conectar_rdp(self):
        if not self.validar_servidores():
            return
        
        bastion_info = self.bastion_frame.get_data()
        servidor_info = self.servidor_frame.get_data()
        
        self.update_status("Abrindo RDP via túnel...")
        threading.Thread(
            target=connections.criar_tunel_rdp,
            args=(bastion_info, servidor_info),
            daemon=True
        ).start()
    
    def on_criar_socks(self):
        bastion_nome = self.bastion_frame.get_selected_server()
        if not bastion_nome or bastion_nome not in self.bastions:
            messagebox.showerror("Erro", "Selecione um bastion válido.")
            return
        
        bastion_info = self.bastion_frame.get_data()
        
        self.update_status("Criando túnel SOCKS...")
        threading.Thread(
            target=connections.criar_tunel_socks,
            args=(bastion_info, 8888),
            daemon=True
        ).start()
    
    def on_upload_rsync(self):
        if not self.validar_servidores():
            return
        
        bastion_info = self.bastion_frame.get_data()
        servidor_info = self.servidor_frame.get_data()
        origem = self.rsync_origem.get()
        destino = self.rsync_destino.get()
        
        if not origem or not destino:
            messagebox.showerror("Erro", "Preencha origem e destino.")
            return
        
        self.update_status("Copiando arquivos via Rsync...")
        threading.Thread(
            target=connections.copiar_rsync,
            args=(bastion_info, servidor_info, origem, destino),
            daemon=True
        ).start()
    
    def on_download_rsync(self):
        if not self.validar_servidores():
            return
        
        bastion_info = self.bastion_frame.get_data()
        servidor_info = self.servidor_frame.get_data()
        origem = self.rsync_destino.get()  # Inverte origem/destino
        destino = self.rsync_origem.get()
        
        if not origem or not destino:
            messagebox.showerror("Erro", "Preencha origem e destino.")
            return
        
        self.update_status("Baixando arquivos via Rsync...")
        threading.Thread(
            target=connections.copiar_rsync,
            args=(bastion_info, servidor_info, origem, destino),
            daemon=True
        ).start()
    
    def procurar_arquivo(self):
        """Abre diálogo para procurar arquivo"""
        messagebox.showinfo("Info", "Funcionalidade de busca será implementada")
    
    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()

def criar_interface():
    """Função principal para criar a interface"""
    app = MainWindow()
    app.run()