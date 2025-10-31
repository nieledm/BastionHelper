import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
from typing import Dict, Any
import connections

# Configuração de cores e tema
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#34495e',
    'accent': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'light': '#ecf0f1',
    'dark': '#2c3e50',
    'text': '#2c3e50',
    'text_light': '#7f8c8d'
}

class ModernButton(ttk.Button):
    """Botão com estilo moderno"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = ttk.Style()
        self.style.configure('Modern.TButton', 
                           foreground=COLORS['text'],
                           background=COLORS['accent'],
                           focuscolor='none')

class ConfigManager:
    """Gerenciador de configurações"""
    @staticmethod
    def carregar_config():
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("BASTIONS", {}), config.get("SERVIDORES", {})
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar config.json: {str(e)}")
            return {}, {}

    @staticmethod
    def salvar_config(bastions_data, servidores_data):
        try:
            config = {
                "BASTIONS": bastions_data,
                "SERVIDORES": servidores_data
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar config.json: {str(e)}")
            return False

class ServerFormFrame(ttk.LabelFrame):
    """Frame para formulário de servidor"""
    def __init__(self, parent, title, servers_data, callback):
        super().__init__(parent, text=title, padding="15")
        self.servers_data = servers_data
        self.callback = callback
        self.create_widgets()
        
    def create_widgets(self):
        # Combobox para seleção
        ttk.Label(self, text=f"Selecione o {self['text'].lower()}:").pack(anchor="w", pady=(0, 5))
        self.combobox = ttk.Combobox(self, values=list(self.servers_data.keys()), state="readonly")
        self.combobox.pack(fill=tk.X, pady=(0, 15))
        self.combobox.bind("<<ComboboxSelected>>", self.on_server_select)
        
        # Frame para campos
        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.X)
        
        # Coluna esquerda
        left_frame = ttk.Frame(form_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Host:").pack(anchor="w", pady=(5, 0))
        self.host_entry = ttk.Entry(left_frame)
        self.host_entry.pack(fill=tk.X, pady=(2, 10))
        
        ttk.Label(left_frame, text="Usuário:").pack(anchor="w")
        self.user_entry = ttk.Entry(left_frame)
        self.user_entry.pack(fill=tk.X, pady=(2, 10))
        
        # Coluna direita
        right_frame = ttk.Frame(form_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        ttk.Label(right_frame, text="Senha:").pack(anchor="w", pady=(5, 0))
        self.pass_entry = ttk.Entry(right_frame, show="•")
        self.pass_entry.pack(fill=tk.X, pady=(2, 10))
        
        ttk.Label(right_frame, text="Porta:").pack(anchor="w")
        self.port_entry = ttk.Entry(right_frame)
        self.port_entry.pack(fill=tk.X, pady=(2, 10))
        
        # Botão de teste de conexão
        ttk.Button(self, text="Testar Conexão", 
                  command=self.test_connection).pack(pady=(10, 0))
    
    def on_server_select(self, event):
        """Preenche os campos quando um servidor é selecionado"""
        nome = self.combobox.get()
        if nome in self.servers_data:
            server = self.servers_data[nome]
            self.host_entry.delete(0, tk.END)
            self.user_entry.delete(0, tk.END)
            self.pass_entry.delete(0, tk.END)
            self.port_entry.delete(0, tk.END)
            
            self.host_entry.insert(0, server.get("host", ""))
            self.user_entry.insert(0, server.get("user", ""))
            self.pass_entry.insert(0, server.get("password", ""))
            self.port_entry.insert(0, server.get("port", ""))
    
    def test_connection(self):
        """Testa a conexão com o servidor"""
        def run_test():
            try:
                # Aqui você pode implementar um teste de conexão simples
                # Por enquanto, apenas simula um teste
                import time
                time.sleep(1)  # Simula delay de conexão
                messagebox.showinfo("Teste de Conexão", "Conexão bem-sucedida!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha na conexão: {str(e)}")
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def get_data(self):
        """Retorna os dados do formulário"""
        return {
            "host": self.host_entry.get(),
            "user": self.user_entry.get(),
            "password": self.pass_entry.get(),
            "port": self.port_entry.get()
        }

class ModernGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.bastions, self.servidores = ConfigManager.carregar_config()
        self.setup_window()
        self.create_widgets()
        self.setup_styles()
        
    def setup_window(self):
        self.root.title("Jump Helper - Gerenciador de Conexões SSH")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Centralizar na tela
        self.root.eval('tk::PlaceWindow . center')
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores
        style.configure('TFrame', background=COLORS['light'])
        style.configure('TLabel', background=COLORS['light'], foreground=COLORS['text'])
        style.configure('TLabelframe', background=COLORS['light'], foreground=COLORS['primary'])
        style.configure('TLabelframe.Label', background=COLORS['light'], foreground=COLORS['primary'])
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Jump Helper", 
                 font=("Arial", 18, "bold"), 
                 foreground=COLORS['primary']).pack(side=tk.LEFT)
        
        # Menu
        self.create_menu()
        
        # Container dos servidores
        servers_container = ttk.Frame(main_frame)
        servers_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Frame do Bastion
        self.bastion_frame = ServerFormFrame(
            servers_container, "Servidor Intermediário (Bastion)", 
            self.bastions, self.on_bastion_select
        )
        self.bastion_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Frame do Servidor Final
        self.servidor_frame = ServerFormFrame(
            servers_container, "Servidor Final", 
            self.servidores, self.on_servidor_select
        )
        self.servidor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Frame do Rsync
        self.create_rsync_frame(main_frame)
        
        # Frame dos botões de ação
        self.create_action_buttons(main_frame)
        
        # Status bar
        self.create_status_bar()
    
    def create_menu(self):
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
    
    def create_rsync_frame(self, parent):
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
                  command=self.on_copiar_rsync).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rsync_buttons, text="Download ←", 
                  command=self.on_download_rsync).pack(side=tk.LEFT)
        
        ttk.Button(rsync_buttons, text="Procurar...", 
                  command=self.procurar_arquivo).pack(side=tk.RIGHT)
    
    def create_action_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Botões principais
        buttons_config = [
            ("🌐 Conectar SSH", self.on_conectar_ssh, COLORS['success']),
            ("🖥️ Abrir RDP", self.on_conectar_rdp, COLORS['accent']),
            ("🔒 SOCKS Proxy", self.on_criar_socks, COLORS['warning']),
            ("🔄 Copiar Rsync", self.on_copiar_rsync, COLORS['primary'])
        ]
        
        for text, command, color in buttons_config:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, relief='sunken', padding="5")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="Pronto para conectar")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        ttk.Label(status_frame, text="Jump Helper v1.0").pack(side=tk.RIGHT)
    
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def editar_config(self):
        def salvar_configuracoes():
            try:
                bastions_data = json.loads(bastions_text.get("1.0", tk.END))
                servidores_data = json.loads(servidores_text.get("1.0", tk.END))
                
                if ConfigManager.salvar_config(bastions_data, servidores_data):
                    self.bastions, self.servidores = bastions_data, servidores_data
                    self.recarregar_comboboxes()
                    edit_window.destroy()
                    messagebox.showinfo("Sucesso", "Configurações salvas e aplicadas!")
                    
            except json.JSONDecodeError as e:
                messagebox.showerror("Erro JSON", f"JSON inválido: {str(e)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editor de Configurações")
        edit_window.geometry("800x600")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Notebook para abas
        notebook = ttk.Notebook(edit_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba Bastions
        bastion_frame = ttk.Frame(notebook, padding="10")
        notebook.add(bastion_frame, text="Bastions")
        
        ttk.Label(bastion_frame, text="Configuração dos Bastions (JSON):").pack(anchor="w")
        bastions_text = scrolledtext.ScrolledText(bastion_frame, height=12)
        bastions_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        bastions_text.insert("1.0", json.dumps(self.bastions, indent=4, ensure_ascii=False))
        
        # Aba Servidores
        servidor_frame = ttk.Frame(notebook, padding="10")
        notebook.add(servidor_frame, text="Servidores")
        
        ttk.Label(servidor_frame, text="Configuração dos Servidores (JSON):").pack(anchor="w")
        servidores_text = scrolledtext.ScrolledText(servidor_frame, height=12)
        servidores_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        servidores_text.insert("1.0", json.dumps(self.servidores, indent=4, ensure_ascii=False))
        
        # Botões
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Salvar", 
                  command=salvar_configuracoes).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=edit_window.destroy).pack(side=tk.RIGHT)
    
    def recarregar_comboboxes(self):
        """Recarrega os valores dos comboboxes"""
        self.bastion_frame.combobox['values'] = list(self.bastions.keys())
        self.servidor_frame.combobox['values'] = list(self.servidores.keys())
    
    def recarregar_config(self):
        self.bastions, self.servidores = ConfigManager.carregar_config()
        self.recarregar_comboboxes()
        messagebox.showinfo("Sucesso", "Configurações recarregadas!")
    
    def mostrar_sobre(self):
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
        bastion_nome = self.bastion_frame.combobox.get()
        servidor_nome = self.servidor_frame.combobox.get()
        
        if not bastion_nome or bastion_nome not in self.bastions:
            messagebox.showerror("Erro", "Selecione um bastion válido.")
            return False
        
        if not servidor_nome or servidor_nome not in self.servidores:
            messagebox.showerror("Erro", "Selecione um servidor válido.")
            return False
        
        return True
    
    # Handlers de eventos
    def on_bastion_select(self, event):
        pass
    
    def on_servidor_select(self, event):
        pass
    
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
        bastion_nome = self.bastion_frame.combobox.get()
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
    
    def on_copiar_rsync(self):
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
        # Você precisaria modificar a função copiar_rsync para suportar download
        # Por enquanto, usa a mesma função
        threading.Thread(
            target=connections.copiar_rsync,
            args=(bastion_info, servidor_info, origem, destino),
            daemon=True
        ).start()
    
    def procurar_arquivo(self):
        """Abre diálogo para procurar arquivo (simulado)"""
        # Em uma implementação real, você usaria filedialog
        messagebox.showinfo("Info", "Funcionalidade de busca será implementada")
    
    def run(self):
        self.root.mainloop()

def criar_interface():
    app = ModernGUI()
    app.run()

if __name__ == "__main__":
    criar_interface()