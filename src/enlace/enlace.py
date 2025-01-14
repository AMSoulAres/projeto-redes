from typing import List, Tuple, Union
import threading
import socket
import numpy as np

from .enquadramento import Enquadramento
from .erros import CorrecaoErros

class CamadaEnlace:
    def __init__(self):
        self.enquadramento = Enquadramento()
        self.deteccao_erros = CorrecaoErros()
        self.correcao_erros = CorrecaoErros()
        
    def transmitir(self, dados: bytes, usar_crc: bool = True, 
                  usar_hamming: bool = True) -> bytes:
        """
        Processa dados para transmissão aplicando enquadramento e 
        detecção/correção de erros.
        
        Args:
            dados: Dados a serem transmitidos
            usar_crc: Flag para usar CRC ao invés de paridade
            usar_hamming: Flag para usar código Hamming
            
        Returns:
            Dados processados prontos para transmissão
        """
        # 1. Aplica correção de erros (Hamming)
        if usar_hamming:
            bits = [int(b) for byte in dados for b in format(byte, '08b')]
            dados_protegidos = self.correcao_erros.hamming_encode(bits)
            # Converte bits de volta para bytes
            dados = bytes([int(''.join(map(str, dados_protegidos[i:i+8])), 2)
                         for i in range(0, len(dados_protegidos), 8)])
        
        # 2. Aplica detecção de erros
        if usar_crc:
            dados, verificacao = self.deteccao_erros.crc32(dados)
        else:
            dados, verificacao = self.deteccao_erros.paridade_par(dados)
            
        # 3. Adiciona verificação aos dados
        dados_com_verificacao = dados + verificacao.to_bytes(4, 'big')
        
        # 4. Aplica enquadramento
        quadro = self.enquadramento.insercao_bytes(dados_com_verificacao)
        
        return quadro

    def receber(self, quadro: bytes, usar_crc: bool = True,
                usar_hamming: bool = True) -> Tuple[bytes, bool]:
        """
        Processa dados recebidos, removendo enquadramento e verificando erros.
        
        Args:
            quadro: Dados recebidos
            usar_crc: Flag para usar CRC ao invés de paridade
            usar_hamming: Flag para usar código Hamming
            
        Returns:
            Tuple com dados processados e flag indicando se houve erros
        """
        # 1. Remove enquadramento
        dados_com_verificacao = self.enquadramento.remover_bytes(quadro)
        
        # 2. Separa dados e verificação
        dados = dados_com_verificacao[:-4]
        verificacao_recebida = int.from_bytes(dados_com_verificacao[-4:], 'big')
        
        # 3. Verifica erros
        if usar_crc:
            _, verificacao_calculada = self.deteccao_erros.crc32(dados)
        else:
            _, verificacao_calculada = self.deteccao_erros.paridade_par(dados)
            
        sem_erros = verificacao_recebida == verificacao_calculada
        
        # 4. Aplica correção de erros se necessário
        if usar_hamming and not sem_erros:
            bits = [int(b) for byte in dados for b in format(byte, '08b')]
            dados_corrigidos, corrigido = self.correcao_erros.hamming_decode(bits)
            if corrigido:
                # Converte bits corrigidos de volta para bytes
                dados = bytes([int(''.join(map(str, dados_corrigidos[i:i+8])), 2)
                             for i in range(0, len(dados_corrigidos), 8)])
                sem_erros = True
                
        return dados, sem_erros
