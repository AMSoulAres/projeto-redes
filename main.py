import sys
import signal
import threading

from src.enlace.simulador import Simulador
from src.interface.inteface import InterfaceGUI

def signal_handler(sig, frame):
    """Manipula o sinal de interrupção (Ctrl+C)."""
    print("\nEncerrando o simulador...")
    simulador.parar()
    sys.exit(0)

if __name__ == "__main__":
    # Registra handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Cria instância do simulador
    simulador = Simulador(host='localhost', port=5000)
    
    # Inicia servidor em uma thread separada
    servidor_thread = threading.Thread(target=simulador.iniciar_servidor)
    servidor_thread.daemon = True  # Thread será encerrada quando o programa principal terminar
    servidor_thread.start()
    
    # Cria e inicia interface gráfica
    interface = InterfaceGUI(simulador)
    interface.iniciar()