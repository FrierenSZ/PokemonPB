"""
Script de teste para verificar se as dependências estão instaladas
"""
import sys

print("Python version:", sys.version)
print("\nTentando importar as bibliotecas...\n")

try:
    import flask
    print("✓ Flask instalado:", flask.__version__)
except ImportError as e:
    print("✗ Flask NÃO instalado:", e)

try:
    import flask_socketio
    print("✓ Flask-SocketIO instalado:", flask_socketio.__version__)
except ImportError as e:
    print("✗ Flask-SocketIO NÃO instalado:", e)

try:
    import requests
    print("✓ Requests instalado:", requests.__version__)
except ImportError as e:
    print("✗ Requests NÃO instalado:", e)

try:
    import eventlet
    print("✓ Eventlet instalado:", eventlet.__version__)
except ImportError as e:
    print("✗ Eventlet NÃO instalado:", e)

print("\n" + "="*50)
print("Se todas as bibliotecas estiverem com ✓, está tudo OK!")
print("Se alguma estiver com ✗, rode: venv\\Scripts\\pip install -r requirements.txt")
