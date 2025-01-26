import socket
import json
import struct
import numpy as np
from CamadaFisica import ModulacaoDigital, ModulacaoPortadora
from CamadaEnlace import CamadaEnlace

class SimuladorReceptor:
    def __init__(self):
        self.mod_digital = ModulacaoDigital()
        self.mod_portadora = ModulacaoPortadora()
        self.camada_enlace = CamadaEnlace([])
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
            tamanho = struct.unpack('!I', self.client_socket.recv(4))[0]
            dados_json = b''
            while len(dados_json) < tamanho:
                chunk = self.client_socket.recv(min(4096, tamanho - len(dados_json)))
                if not chunk:
                    break
                dados_json += chunk

            if not dados_json:
                return False, "Conexão encerrada pelo cliente"
            
            dados = json.loads(dados_json.decode('utf-8'))
            enquadramento = dados['enquadramento']
            deteccao = dados['deteccao']
            correcao = dados['correcao']
            mod_digital = dados['modulacao_digital']
            mod_portadora = dados['modulacao_portadora']
            sinal_digital = np.array(dados['sinal_digital'])
            tempo_sinal_digital = np.array(dados['tempo_sinal_digital'])
            sinal_portadora = np.array(dados['sinal_portadora'])
            tempo_sinal_portadora = np.array(dados['tempo_sinal_portadora'])
            mod_portadora = dados['modulacao_portadora']
            sinal_digital_erro = np.array(dados['sinal_digital_erro'])
            tempo_sinal_digital_erro = np.array(dados['tempo_sinal_digital_erro'])
            sinal_portadora_erro = np.array(dados['sinal_portadora_erro'])
            tempo_sinal_portadora_erro = np.array(dados['tempo_sinal_portadora_erro'])

            # Configuração da camada de enlace
            self.camada_enlace.set_detection_correction(deteccao)
            self.camada_enlace.set_hamming(correcao)

            # Decodificação da modulação da portadora
            if mod_portadora == "ASK":
                bits_portadora = self.mod_portadora.ask_decode(sinal_portadora)
            elif mod_portadora == "FSK":
                bits_portadora = self.mod_portadora.fsk_decode(sinal_portadora)
            elif mod_portadora == "8-QAM":
                bits_portadora = self.mod_portadora.qam8_decode(sinal_portadora)
            else:
                raise ValueError("Modulação desconhecida")

            # Decodificação da modulação digital
            if mod_digital == "NRZ-Polar":
                bits_recebidos = self.mod_digital.nrz_polar_decode(sinal_digital)
            elif mod_digital == "Manchester":
                bits_recebidos = self.mod_digital.manchester_decode(sinal_digital)
            elif mod_digital == "Bipolar":
                bits_recebidos = self.mod_digital.bipolar_decode(sinal_digital)
            else:
                raise ValueError("Modulação desconhecida")

            # Desenquadramento dos dados
            if enquadramento == "Contagem de Caracteres":
                bits_desenquadrados = self.camada_enlace.desenquadrar_contagem(bits_recebidos)
            elif enquadramento == "Inserção de Bytes":
                bits_desenquadrados = self.camada_enlace.desenquadrar_insercao(bits_recebidos)
            else:
                raise ValueError("Enquadramento desconhecido")
            
            # Verificação de erros
            if deteccao == "Bit de paridade par":
                erro_detectado = True
                erro = self.camada_enlace.verificar_paridade(bits_desenquadrados)
            elif deteccao == "CRC-32":
                erro_detectado = True
                erro = self.camada_enlace.verificar_crc(bits_desenquadrados)

            if correcao and deteccao != "Nenhum":
                bits_corrigidos = self.camada_enlace.corrigir_hamming(erro)
            elif correcao and deteccao == "Nenhum":
                bits_corrigidos = self.camada_enlace.corrigir_hamming(bits_desenquadrados)

            if erro_detectado and not correcao:
                # Conversão dos bits desenquadrados para ASCII
                mensagem = ''.join(chr(int(bits_desenquadrados[i:i+8], 2)) for i in range(0, len(bits_desenquadrados), 8))
                return True, (mensagem, mod_digital, mod_portadora, bits_recebidos, tempo_sinal_digital_erro, sinal_digital_erro, tempo_sinal_portadora_erro, sinal_portadora_erro)
                
            elif erro_detectado and correcao:
                # Conversão dos bits desenquadrados para ASCII
                mensagem = ''.join(chr(int(bits_corrigidos[i:i+8], 2)) for i in range(0, len(bits_corrigidos), 8))
                return True, (mensagem, mod_digital, mod_portadora, bits_recebidos, tempo_sinal_digital, sinal_digital, tempo_sinal_portadora, sinal_portadora)
            else:
                # Conversão dos bits desenquadrados para ASCII
                mensagem = ''.join(chr(int(bits_desenquadrados[i:i+8], 2)) for i in range(0, len(bits_desenquadrados), 8))
                return True, (mensagem, mod_digital, mod_portadora, bits_recebidos, tempo_sinal_digital, sinal_digital, tempo_sinal_portadora, sinal_portadora)


        except Exception as e:
            return False, f"Erro ao receber dados: {str(e)}"