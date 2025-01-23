import socket
import json
from CamadaFisica import ModulacaoDigital, ModulacaoPortadora
from CamadaEnlace import CamadaEnlace

class SimuladorReceptor:
    def __init__(self):
        self.mod_digital = ModulacaoDigital()
        self.mod_portadora = ModulacaoPortadora()
        self.camada_enlace = CamadaEnlace(["CRC-32", "Paridade"])
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = None
        self.running = True

    def iniciar_servidor(self, ip, port):
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((ip, port))
            self.server_socket.listen(1)
            return True, f"Servidor iniciado em {ip}:{port}"
        except Exception as e:
            return False, f"Erro ao iniciar servidor: {str(e)}"

    def parar_servidor(self):
        try:
            self.running = False
            self.server_socket.close()
            if self.client_socket:
                self.client_socket.close()
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return True, "Servidor parado"
        except Exception as e:
            return False, f"Erro ao parar servidor: {str(e)}"

    def aceitar_conexoes(self):
        while self.running:
            try:
                self.client_socket, address = self.server_socket.accept()
                return True, f"Cliente conectado de {address}"
            except Exception as e:
                if self.running:
                    return False, f"Erro na conexão: {str(e)}"
                break

    def receber_dados(self):
        try:
            data = self.client_socket.recv(4096)
            if not data:
                return False, "Conexão encerrada pelo cliente"
            
            dados = json.loads(data.decode('utf-8'))
            texto = dados['texto']
            mod_digital = dados['modulacao_digital']
            mod_portadora = dados['modulacao_portadora']
            quadros = dados['quadros']

            # Desenquadramento dos dados
            bits_recebidos = self.camada_enlace.desenquadrar_contagem(quadros)

            return True, (texto, mod_digital, mod_portadora, bits_recebidos)
        except Exception as e:
            return False, f"Erro ao receber dados: {str(e)}"