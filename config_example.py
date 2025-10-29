# config.py

# Dicionário de bastions disponíveis
BASTIONS = {
    "Bastion Principal": {
        "host": "bastion1.exemplo.com",
        "user": "usuario1",
        "password": "senha1",
        "port": 22
    },
    "Bastion Backup": {
        "host": "bastion2.exemplo.com",
        "user": "usuario2",
        "password": "senha2",
        "port": 2323
    }
}

# Lista predefinida de servidores finais
SERVIDORES = {
    "Servidor A": "10.0.0.10",
    "Servidor B": "10.0.0.20",
}