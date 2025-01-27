import binascii
from bitarray import bitarray

class CamadaEnlace:
    def __init__(self, detection_correction):
        self.detection_methods = []
        self.detection_size = 0
        for method in detection_correction:
            if method == "Paridade":
                self.detection_methods.append(self.adicionar_paridade)
                self.detection_size += 8
            elif method == "CRC-32":
                self.detection_methods.append(self.adicionar_crc)
                self.detection_size += 32
        self.hamming_enabled = "Hamming" in detection_correction

    def set_hamming(self, enabled):
        self.hamming_enabled = enabled
    
    def set_detection_correction(self, methods):
        for method in methods:
            if method == "Paridade":
                self.detection_methods.append(self.adicionar_paridade)
                self.detection_size += 8
            elif method == "CRC-32":
                self.detection_methods.append(self.adicionar_crc)
                self.detection_size += 32

    # Transmissão
    def enquadrar_contagem(self, dados, tamanho_maximo):
        """ Realiza enquadramento utilizando contagem de bytes """
        quadros = []
        while dados:
            payload = dados[:tamanho_maximo]
            dados = dados[tamanho_maximo:]
            for method in self.detection_methods:
                payload = method(payload)
            if self.hamming_enabled:
                payload = self.codificar_hamming(payload)
            
            # Calcula o tamanho do payload em bytes (arredondando para cima)
            tamanho_bytes = (len(payload) + 7) // 8  # Arredonda para cima
            quadro = f"{tamanho_bytes:08b}" + payload
            quadros.append(quadro)
        return quadros

    def enquadrar_insercao(self, dados, tamanho_maximo, delimitador="01111110", escape="00100011"):
        """ Realiza enquadramento utilizando inserção de flags """
        quadros = []
        while dados:
            payload = dados[:tamanho_maximo]
            dados = dados[tamanho_maximo:]
            escaped_payload = ""
            for byte in [payload[i:i+8] for i in range(0, len(payload), 8)]:
                if byte in [delimitador, escape]:
                    escaped_payload += escape
                escaped_payload += byte
            for method in self.detection_methods:
                escaped_payload = method(escaped_payload)
            if self.hamming_enabled:
                escaped_payload = self.codificar_hamming(escaped_payload)
            quadro = delimitador + escaped_payload + delimitador
            quadros.append(quadro)
        return quadros

    def adicionar_paridade(self, dados):
        """ Adiciona bit de paridade ao final dos dados """
        bits = bitarray(dados)
        paridade = bits.count() % 2
        return dados + str(paridade)

    def adicionar_crc(self, dados):
        bits = bitarray(dados)
        # Padding para múltiplo de 8
        padding = (8 - (len(bits) % 8)) % 8
        bits.extend([0] * padding)
        crc = binascii.crc32(bits.tobytes()) & 0xFFFFFFFF
        return dados + f"{crc:032b}"

    def codificar_hamming(self, dados):
        """ Adiciona bits de Hamming para correção de erros """
        # Converte dados para lista de bits
        bits = [int(x) for x in dados]
        n = len(bits)
        
        # Calcula quantidade de bits de paridade necessários
        m = 0
        while (1 << m) < (n + m + 1):
            m += 1
        
        # Cria vetor com espaço para bits de paridade
        hamming = [0] * (n + m)
        
        # Posiciona bits de dados
        j = 0
        for i in range(1, len(hamming) + 1):
            if (i & (i - 1)) != 0:  # Não é potência de 2
                hamming[i - 1] = bits[j]
                j += 1
        
        # Calcula bits de paridade
        for i in range(m):
            pos = (1 << i) - 1
            valor = 0
            for j in range(pos, len(hamming), 1 << (i + 1)):
                for k in range(j, min(j + (1 << i), len(hamming))):
                    valor ^= hamming[k]
            hamming[pos] = valor
        
        # Converte para string binária
        return ''.join(map(str, hamming))

    # Recepção
    def desenquadrar_contagem(self, quadros):
        quadros = prepara(quadros)
        dados = ""
        while len(quadros) > 8:
            tamanho_bytes = int(quadros[:8], 2)
            tamanho_bits = tamanho_bytes * 8
            payload = quadros[8:8 + tamanho_bits]
            quadros = quadros[8 + tamanho_bits:]
            dados += payload
        return dados

    def desenquadrar_insercao(self, quadros, delimitador="01111110", escape="00100011"):
        """Desenquadra os dados utilizando inserção de flags"""
        # Transforma a entrada em uma única string
        quadros = prepara(quadros)
        dados = ""
        
        # Divide os quadros usando o delimitador
        quadros_split = quadros.split(delimitador)
        
        # Remove quadros vazios (gerados por delimitadores consecutivos)
        quadros_split = [q for q in quadros_split if q]
        
        for quadro in quadros_split:
            desescaped_payload = ""
            i = 0
            
            while i < len(quadro):
                byte = quadro[i:i + 8]
                if byte == escape:
                    # Ignora o próximo byte (é um byte escapado)
                    i += 8
                    byte = quadro[i:i + 8]
                desescaped_payload += byte
                i += 8
            
            # Aplica decodificação Hamming se habilitado
            if self.hamming_enabled:
                desescaped_payload = self.decodificar_hamming(desescaped_payload)
            
            # Verifica métodos de detecção
            for method in self.detection_methods:
                if not method(desescaped_payload):
                    raise ValueError("Erro detectado no quadro")

            
            # Adiciona o payload decodificado aos dados finais
            dados += desescaped_payload
        
        return dados


    def verificar_paridade(self, dados):
        """ Verifica se o bit de paridade é válido """
        # Garante que o dado recebido é um string de bits
        bits = bitarray(dados[:-1])  # Todos os bits, exceto o último
        paridade = int(dados[-1])  # Último bit como paridade
        # Conta os bits 1 no payload e verifica a paridade
        return bits.count(1) % 2 == paridade

    def verificar_crc(self, dados, contagem):
        """Verifica CRC de múltiplos quadros concatenados e retorna os payloads válidos."""
        crc_check = True  # Inicializa o flag para CRC
        payload_final = ""  # Para armazenar os payloads concatenados
        
        while len(dados) >= 48:  # Cada quadro tem 48 bits (16 bits de payload + 32 bits de CRC)
            # Extrai o payload e o CRC do quadro
            payload = dados[:16]  # Primeiro 16 bits são o payload
            crc_recebido = int(dados[16:48], 2)  # Próximos 32 bits são o CRC
            
            # Calcula o CRC do payload
            bits = bitarray(payload)
            padding = (8 - (len(bits) % 8)) % 8  # Adiciona padding para múltiplos de 8 bits
            bits.extend([0] * padding)
            crc_calculado = binascii.crc32(bits.tobytes()) & 0xFFFFFFFF

            # Verifica se o CRC é válido
            if crc_calculado == crc_recebido:
                payload_final += payload  # Adiciona ao resultado apenas se o CRC for válido
            else:
                crc_check = False  # Marca como inválido se algum CRC falhar

            # Remove o quadro processado da string
            dados = dados[48:]  # Move para o próximo quadro (48 bits por quadro)

        if contagem:
            payload_final += dados[:-32]
        else:
            payload_final =+ dados
        # Retorna os dados processados
        return crc_check, payload_final





    def decodificar_hamming(self, dados):
        """ Decodifica bits de Hamming e corrige um erro. Retorna os bits corrigidos como uma lista de inteiros. """
        # Converte dados para lista de bits
        bits = [int(x) for x in dados]
        
        # Calcula quantidade de bits de paridade
        m = 0
        while (1 << m) < len(bits) + 1:
            m += 1
        
        # Verifica posição do erro
        erro = 0
        for i in range(m):
            pos = (1 << i) - 1
            valor = 0
            for j in range(pos, len(bits), 1 << (i + 1)):
                for k in range(j, min(j + (1 << i), len(bits))):
                    valor ^= bits[k]
            if valor != 0:
                erro += (1 << i)
        
        # Corrige erro apenas se estiver dentro do intervalo
        if 0 < erro <= len(bits):
            bits[erro - 1] ^= 1  # Inverte o bit para corrigir o erro
        
        # Recupera bits de dados originais
        dados_recuperados = []
        for i in range(1, len(bits) + 1):
            if (i & (i - 1)) != 0:  # Ignora potências de 2 (bits de paridade)
                dados_recuperados.append(bits[i - 1])
        
        return dados_recuperados


def prepara(bits):
    """ Converte um array de bits (int) em quadros (strings) para a camada de enlace """
    # Converte a lista de bits em uma única string
    quadros = ''.join(map(str, bits))
    
    # Quebra a string em quadros com tamanho fixo 
    return quadros


# Exemplo de uso
if __name__ == "__main__":
    camada_enlace = CamadaEnlace(["CRC-32"])     #"CRC-32", "Paridade"])

    dados = "1010101011110000"
    #"1010101011110000"

    # Enquadramento e transmissão
    quadros = camada_enlace.enquadrar_contagem(dados, 16)
    print("Quadros transmitidos:", quadros)

    # Recepção e desenquadramento
    dados_recebidos = camada_enlace.desenquadrar_contagem(quadros)
    print("Dados recebidos:", dados_recebidos)
