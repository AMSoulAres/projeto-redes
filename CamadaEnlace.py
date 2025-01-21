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
            # print("Payload original:", payload)
            for method in self.detection_methods:
                payload = method(payload)
                # print("Após método de detecção:", payload)
            if self.hamming_enabled:
                payload = self.codificar_hamming(payload)
                # print("Após Hamming:", payload)
            tamanho_payload = len(payload) // 8
            quadro = f"{tamanho_payload:08b}" + payload
            # print("Quadro final:", quadro)
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
        bits = bitarray(dados)
        hamming_bits = bitarray()
        i, j = 0, 1
        while i < len(bits):
            if j & (j - 1) == 0:
                hamming_bits.append(0)
            else:
                hamming_bits.append(bits[i])
                i += 1
            j += 1
        for k in range(len(hamming_bits)):
            if (k + 1) & (k + 2) == 0:
                continue
            value = 0
            for m in range(k + 1, len(hamming_bits) + 1):
                if m & (k + 1):
                    value ^= hamming_bits[m - 1]
            hamming_bits[k] = value
        return hamming_bits.to01()

    # Recepção
    def desenquadrar_contagem(self, quadros):
        """ Desenquadra os dados utilizando contagem de bytes """
        dados = ""
        for quadro in quadros:
            tamanho = int(quadro[:8], 2) * 8
            payload = quadro[8:8 + tamanho]
            if self.hamming_enabled:
                payload = self.decodificar_hamming(payload)
            for method in self.detection_methods:
                if not method(payload):
                    raise ValueError("Erro detectado no quadro")
            dados += payload
        return dados

    def desenquadrar_insercao(self, quadros, delimitador="01111110", escape="00100011"):
        """ Desenquadra os dados utilizando inserção de flags """
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
        bits = bitarray(dados)
        erro = 0
        j = 1
        while j <= len(bits):
            if j & (j - 1) == 0:
                paridade = 0
                for i in range(j, len(bits) + 1):
                    if i & j:
                        paridade ^= bits[i - 1]
                if paridade:
                    erro += j
            j *= 2
        if erro:
            bits[erro - 1] ^= 1
        return bits.to01()


# Exemplo de uso
if __name__ == "__main__":
    camada_enlace = CamadaEnlace(["Paridade"])     #"CRC-32", "Hamming"])

    dados = "1010101011110000"

    # Enquadramento e transmissão
    quadros = camada_enlace.enquadrar_contagem(dados, 16)
    print("Quadros transmitidos:", quadros)

    # Recepção e desenquadramento
    dados_recebidos = camada_enlace.desenquadrar_contagem(quadros)
    print("Dados recebidos:", dados_recebidos)
