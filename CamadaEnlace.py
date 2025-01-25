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

    # Transmissão
    def enquadrar_contagem(self, dados, tamanho_maximo):
        """ Realiza enquadramento utilizando contagem de bytes """
        quadros = []
        while dados:
            payload = dados[:tamanho_maximo]
            dados = dados[tamanho_maximo:]
            print("Payload original:", payload)
            for method in self.detection_methods:
                payload = method(payload)
                print("Após método de detecção:", payload)
            if self.hamming_enabled:
                payload = self.codificar_hamming(payload)
                print("Após Hamming:", payload)
            
            # Calcula o tamanho do payload em bytes (arredondando para cima)
            tamanho_bytes = (len(payload) + 7) // 8  # Arredonda para cima
            quadro = f"{tamanho_bytes:08b}" + payload
            print("Quadro final:", quadro)
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
        """ Adiciona CRC-32 ao final dos dados """
        crc = binascii.crc32(bitarray(dados).tobytes()) & 0xFFFFFFFF
        crc_bits = f"{crc:032b}"
        return dados + crc_bits

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
        for quadro in quadros:
            # Converte os 8 primeiros bits para tamanho do payload em bytes
            tamanho_bytes = int(quadro[:8], 2)
            
            # Calcula o tamanho em bits (8 bits por byte)
            tamanho_bits = tamanho_bytes * 8
            
            # Extrai o payload completo
            payload = quadro[8:8 + tamanho_bits]
            
            # Aplica decodificação Hamming se habilitado
            if self.hamming_enabled:
                payload = self.decodificar_hamming(payload)
                print("Após decodificar Hamming:", payload)
            
            # Verifica métodos de detecção
            for method in self.detection_methods:
                if method == self.adicionar_crc:
                    # Remove o CRC-32 (últimos 32 bits) após a verificação
                    if not self.verificar_crc(payload):
                        raise ValueError("Erro detectado no quadro (CRC-32 inválido)")
                    payload = payload[:-32]
                elif method == self.adicionar_paridade:
                    # Remove o bit de paridade (último bit) após a verificação
                    if not self.verificar_paridade(payload):
                        raise ValueError("Erro detectado no quadro (Paridade inválida)")
                    payload = payload[:-1]
            
            dados += payload

        return dados

    def desenquadrar_insercao(self, quadros, delimitador="01111110", escape="00100011"):
        """ Desenquadra os dados utilizando inserção de flags """
        quadros = prepara(quadros)
        dados = ""
        for quadro in quadros:
            payload = quadro[len(delimitador):-len(delimitador)]
            desescaped_payload = ""
            i = 0
            while i < len(payload):
                byte = payload[i:i + 8]
                if byte == escape:
                    i += 8
                    byte = payload[i:i + 8]
                desescaped_payload += byte
                i += 8
            if self.hamming_enabled:
                desescaped_payload = self.decodificar_hamming(desescaped_payload)
            for method in self.detection_methods:
                if not method(desescaped_payload):
                    raise ValueError("Erro detectado no quadro")
            
            if self.adicionar_crc in self.detection_methods:
                # Remove o CRC-32 (últimos 32 bits) após a verificação
                desescaped_payload = desescaped_payload[:-32]
            
            dados += desescaped_payload
        return dados

    def verificar_paridade(self, dados):
        """ Verifica se o bit de paridade é válido """
        bits = bitarray(dados[:-1])
        paridade = int(dados[-1])
        return bits.count() % 2 == paridade

    def verificar_crc(self, dados):
        """ Verifica se o CRC-32 é válido """
        crc_calculado = binascii.crc32(bitarray(dados[:-32]).tobytes()) & 0xFFFFFFFF
        crc_recebido = int(dados[-32:], 2)
        return crc_calculado == crc_recebido

    def decodificar_hamming(self, dados):
        """ Decodifica bits de Hamming e corrige um erro """
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
            bits[erro - 1] ^= 1
        
        # Recupera bits de dados originais
        dados_recuperados = []
        for i in range(1, len(bits) + 1):
            if (i & (i - 1)) != 0:  # Não é potência de 2
                dados_recuperados.append(bits[i - 1])
        
        return ''.join(map(str, dados_recuperados))

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
