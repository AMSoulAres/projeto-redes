import socket
import json
from CamadaFisica import ModulacaoDigital, ModulacaoPortadora
from CamadaEnlace import CamadaEnlace

class Simulador:
    def __init__(self):
        self.mod_digital = ModulacaoDigital()
        self.mod_portadora = ModulacaoPortadora()
        self.camada_enlace = CamadaEnlace(["CRC-32", "Paridade"])
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def conectar(self, ip, port):
        try:
            self.socket.connect((ip, port))
            self.connected = True
            return True, f"Conectado ao receptor em {ip}:{port}"
        except Exception as e:
            return False, f"Erro na conexão: {str(e)}"

    def desconectar(self):
        try:
            self.socket.close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connected = False
            return True, "Desconectado do receptor"
        except Exception as e:
            return False, f"Erro ao desconectar: {str(e)}"

    def transmitir(self, texto, mod_digital, mod_portadora):
        try:
            # Gera bits a partir do texto
            bits = ''.join(format(byte, '08b') for byte in texto.encode('utf-8'))
            
            # Enquadramento dos dados
            quadros = self.camada_enlace.enquadrar_contagem(bits, 16)

            # Aplica modulação digital selecionada
            if mod_digital == "NRZ-Polar":
                tempo, sinal = self.mod_digital.nrz_polar(bits)
            elif mod_digital == "Manchester":
                tempo, sinal = self.mod_digital.manchester(bits)
            else:  # Bipolar
                tempo, sinal = self.mod_digital.bipolar(bits)

            # Aplica a modulação da portadora
            if mod_portadora == "ASK":
                tempo_carrier, sinal_carrier = self.mod_portadora.ask(bits)
            elif mod_portadora == "FSK":
                tempo_carrier, sinal_carrier = self.mod_portadora.fsk(bits)
            else:  # 8-QAM
                tempo_carrier, sinal_carrier = self.mod_portadora.qam8(bits)

            # Prepara os dados para transmissão
            dados = {
                'texto': texto,
                'modulacao_digital': mod_digital,
                'modulacao_portadora': mod_portadora,
                'quadros': quadros
            }

            # Envia os dados
            self.socket.sendall(json.dumps(dados).encode('utf-8'))

            return True, (tempo, sinal, tempo_carrier, sinal_carrier)
        except Exception as e:
            return False, f"Erro na transmissão: {str(e)}"