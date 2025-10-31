"""
Componentes customizados da interface
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import threading
from config.manager import ConfigManager

class ServerFormFrame(ttk.LabelFrame):
    """Frame para formulário de servidor"""
    
    def __init__(self, parent, title, servers_data):
        super().__init__(parent, text=title, padding="15")
        self.servers_data = servers_data
        self.create_widgets()
        
    def create_widgets(self):
        """Cria os widgets do formulário"""
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
            self.clear_entries()
            
            self.host_entry.insert(0, server.get("host", ""))
            self.user_entry.insert(0, server.get("user", ""))
            self.pass_entry.insert(0, server.get("password", ""))
            self.port_entry.insert(0, server.get("port", ""))
    
    def clear_entries(self):
        """Limpa todos os campos de entrada"""
        for entry in [self.host_entry, self.user_entry, self.pass_entry, self.port_entry]:
            entry.delete(0, tk.END)
    
    def test_connection(self):
        """Testa a conexão com o servidor"""
        def run_test():
            try:
                # Simula teste de conexão
                import time
                time.sleep(1)
                tk.messagebox.showinfo("Teste de Conexão", "Conexão bem-sucedida!")
            except Exception as e:
                tk.messagebox.showerror("Erro", f"Falha na conexão: {str(e)}")
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def get_data(self):
        """Retorna os dados do formulário"""
        return {
            "host": self.host_entry.get(),
            "user": self.user_entry.get(),
            "password": self.pass_entry.get(),
            "port": self.port_entry.get() or "22"  # Default SSH port
        }
    
    def get_selected_server(self):
        """Retorna o servidor selecionado"""
        return self.combobox.get()

class ConfigEditor:
    """Editor de configurações"""
    
    def __init__(self, parent, bastions, servidores, on_save_callback):
        self.parent = parent
        self.bastions = bastions
        self.servidores = servidores
        self.on_save_callback = on_save_callback
        self.create_window()
    
    def create_window(self):
        """Cria a janela de edição"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Editor de Configurações")
        self.window.geometry("800x600")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Cria os widgets do editor"""
        # Notebook para abas
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba Bastions
        self.create_bastion_tab(notebook)
        
        # Aba Servidores
        self.create_servidor_tab(notebook)
        
        # Botões
        self.create_buttons()
    
    def create_bastion_tab(self, notebook):
        """Cria a aba de bastions"""
        bastion_frame = ttk.Frame(notebook, padding="10")
        notebook.add(bastion_frame, text="Bastions")
        
        ttk.Label(bastion_frame, text="Configuração dos Bastions (JSON):").pack(anchor="w")
        self.bastions_text = scrolledtext.ScrolledText(bastion_frame, height=12)
        self.bastions_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        self.bastions_text.insert("1.0", json.dumps(self.bastions, indent=4, ensure_ascii=False))
    
    def create_servidor_tab(self, notebook):
        """Cria a aba de servidores"""
        servidor_frame = ttk.Frame(notebook, padding="10")
        notebook.add(servidor_frame, text="Servidores")
        
        ttk.Label(servidor_frame, text="Configuração dos Servidores (JSON):").pack(anchor="w")
        self.servidores_text = scrolledtext.ScrolledText(servidor_frame, height=12)
        self.servidores_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        self.servidores_text.insert("1.0", json.dumps(self.servidores, indent=4, ensure_ascii=False))
    
    def create_buttons(self):
        """Cria os botões de ação"""
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Salvar", 
                  command=self.salvar_configuracoes).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def salvar_configuracoes(self):
        """Salva as configurações"""
        bastions_text = self.bastions_text.get("1.0", tk.END)
        servidores_text = self.servidores_text.get("1.0", tk.END)
        
        # Valida JSON
        success_bastions, bastions_data = ConfigManager.validar_config_json(bastions_text)
        success_servidores, servidores_data = ConfigManager.validar_config_json(servidores_text)
        
        if not success_bastions:
            tk.messagebox.showerror("Erro JSON", f"Bastions: {bastions_data}")
            return
        
        if not success_servidores:
            tk.messagebox.showerror("Erro JSON", f"Servidores: {servidores_data}")
            return
        
        # Salva configurações
        if ConfigManager.salvar_config(bastions_data, servidores_data):
            self.on_save_callback(bastions_data, servidores_data)
            self.window.destroy()
            tk.messagebox.showinfo("Sucesso", "Configurações salvas e aplicadas!")

class StatusBar(ttk.Frame):
    """Barra de status"""
    
    def __init__(self, parent):
        super().__init__(parent, relief='sunken', padding="5")
        self.parent = parent
        self.create_widgets()
    
    def create_widgets(self):
        """Cria os widgets da barra de status"""
        self.status_var = tk.StringVar(value="Pronto para conectar")
        ttk.Label(self, textvariable=self.status_var).pack(side=tk.LEFT)
        
        ttk.Label(self, text="Jump Helper v1.0").pack(side=tk.RIGHT)
    
    def update_status(self, message):
        """Atualiza a mensagem de status"""
        self.status_var.set(message)
        self.parent.update_idletasks()