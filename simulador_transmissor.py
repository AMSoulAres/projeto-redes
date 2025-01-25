import socket
import json
import struct
from CamadaFisica import ModulacaoDigital, ModulacaoPortadora
from CamadaEnlace import CamadaEnlace

class Simulador:
    def __init__(self):
        self.mod_digital = ModulacaoDigital()
        self.mod_portadora = ModulacaoPortadora()
        self.camada_enlace = CamadaEnlace([])
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def configurar_camada_enlace(self, metodos):
        self.camada_enlace = CamadaEnlace(metodos)

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

    def transmitir(self, texto, mod_digital, mod_portadora, enquadramento, deteccao, correcao):
        try:
            # Gera bits a partir do texto
            bits = ''.join(format(byte, '08b') for byte in texto.encode('utf-8'))
            
            # Enquadramento dos dados
            if enquadramento == "Contagem de Caracteres":
                quadros = self.camada_enlace.enquadrar_contagem(bits, 16)
            elif enquadramento == "Inserção de Bytes":
                quadros = self.camada_enlace.enquadrar_insercao(bits, 16)
            else:
                raise ValueError("Uma forma de enquadramento deve ser selecionada.")

            # Aplica modulação digital selecionada
            if mod_digital == "NRZ-Polar":
                tempo, sinal = self.mod_digital.nrz_polar(quadros)
            elif mod_digital == "Manchester":
                tempo, sinal = self.mod_digital.manchester(quadros)
            elif mod_digital == "Bipolar":
                tempo, sinal = self.mod_digital.bipolar(quadros)
            else:
                raise ValueError("Uma forma de modulação digital deve ser selecionada.")
 
            # Aplica a modulação da portadora
            if mod_portadora == "ASK":
                tempo_carrier, sinal_carrier = self.mod_portadora.ask(quadros)
            elif mod_portadora == "FSK":
                tempo_carrier, sinal_carrier = self.mod_portadora.fsk(quadros)
            elif mod_portadora == "8-QAM":
                tempo_carrier, sinal_carrier = self.mod_portadora.qam8(quadros)
            else:
                raise ValueError("Uma forma de modulação digital deve ser selecionada.")
            
            # Prepara os dados para transmissão
            dados = {
                'enquadramento': enquadramento,
                'deteccao': deteccao,
                'correcao': correcao,
                'modulacao_digital': mod_digital,
                'modulacao_portadora': mod_portadora,
                'sinal_digital': sinal.tolist(),
                'tempo_sinal_digital': tempo.tolist(),
                'sinal_portadora': sinal_carrier.tolist(),
                'tempo_sinal_portadora': tempo_carrier.tolist()
            }

            # Envia os dados
            dados_json = json.dumps(dados)
            tamanho = len(dados_json)
            self.socket.sendall(struct.pack('!I', tamanho))  # Envia o tamanho primeiro
            self.socket.sendall(dados_json.encode('utf-8'))  # Depois envia os dados

            return True, (tempo, sinal, tempo_carrier, sinal_carrier)
        except Exception as e:
            return False, f"Erro na transmissão: {str(e)}"