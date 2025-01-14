import struct


class Enquadramento:
    def __init__(self):
        self.flag = b'\x7E'  # Flag de início/fim (byte 126)
        self.esc = b'\x7D'   # Byte de escape (byte 125)

    def contagem_caracteres(self, dados: bytes) -> bytes:
        """
        Implementa enquadramento por contagem de caracteres.
        
        Args:
            dados: Bytes a serem enquadrados
            
        Returns:
            Bytes enquadrados com contagem
        """
        quadros = []
        tamanho_max = 1024  # Tamanho máximo do quadro
        
        for i in range(0, len(dados), tamanho_max):
            quadro = dados[i:i+tamanho_max]
            tamanho = len(quadro)
            # Adiciona o tamanho como um inteiro de 2 bytes no início
            quadro_com_tamanho = struct.pack('>H', tamanho) + quadro
            quadros.append(quadro_com_tamanho)
            
        return b''.join(quadros)

    def insercao_bytes(self, dados: bytes) -> bytes:
        """
        Implementa enquadramento por inserção de bytes.
        
        Args:
            dados: Bytes a serem enquadrados
            
        Returns:
            Bytes enquadrados com flags e escapes
        """
        resultado = bytearray()
        resultado.extend(self.flag)  # Flag de início
        
        for byte in dados:
            if byte == int.from_bytes(self.flag, 'big') or byte == int.from_bytes(self.esc, 'big'):
                resultado.extend(self.esc)
            resultado.append(byte)
            
        resultado.extend(self.flag)  # Flag de fim
        return bytes(resultado)
