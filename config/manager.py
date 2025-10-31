"""
Gerenciador de configurações
"""
import json
import tkinter.messagebox as messagebox

class ConfigManager:
    """Gerenciador de configurações"""
    
    @staticmethod
    def carregar_config():
        """
        Carrega as configurações do arquivo config.json
        
        Returns:
            tuple: (bastions, servidores) ou ({}, {}) em caso de erro
        """
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("BASTIONS", {}), config.get("SERVIDORES", {})
        except FileNotFoundError:
            messagebox.showwarning("Configuração", "Arquivo config.json não encontrado. Criando um novo.")
            return {}, {}
        except json.JSONDecodeError as e:
            messagebox.showerror("Erro", f"Erro ao decodificar config.json: {str(e)}")
            return {}, {}
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar config.json: {str(e)}")
            return {}, {}

    @staticmethod
    def salvar_config(bastions_data, servidores_data):
        """
        Salva as configurações no arquivo config.json
        
        Args:
            bastions_data (dict): Dados dos bastions
            servidores_data (dict): Dados dos servidores
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
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

    @staticmethod
    def validar_config_json(json_text):
        """
        Valida se o texto é um JSON válido
        
        Args:
            json_text (str): Texto para validar
            
        Returns:
            tuple: (bool, dict/str) Sucesso e dados ou mensagem de erro
        """
        try:
            data = json.loads(json_text)
            return True, data
        except json.JSONDecodeError as e:
            return False, f"JSON inválido: {str(e)}"