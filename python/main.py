import serial
import struct
import time
import numpy as np
from signal_teste import  gerar_sinal_com_harmonicas
import matplotlib.pyplot as plt 

# --- CONFIGURACOES ---
# Altere esta para a porta COM correta do seu microcontrolador
SERIAL_PORT = 'COM6'
BAUD_RATE = 115200
print(serial.__file__)
Tam_vect = 1000
amostragemADC = 200000000 / 8000
# --- DEFINICOES DO PROTOCOLO (devem ser identicas as do C) ---
# Comandos (do enum SCI_Command_e)
CMD_RECEIVE_INT = 1 # Comando para o PC enviar um int para o 28379D
CMD_SEND_INT    = 2 # Comando para o PC pedir um int para o 28379D


def main():
    """Funcao principal que gerencia a conexao e o menu do usuario."""
    print("--- Terminal de Teste SCI para 28379D ---")
    
    try:
        # Abre a porta serial usando um bloco 'with' para garantir que ela seja fechada
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
            print(f"Porta serial {SERIAL_PORT} aberta com sucesso a {BAUD_RATE} bps.")
            time.sleep(1) # Um pequeno tempo para a serial estabilizar

            while True:
                print("\n----- MENU -----")
                print("1. Enviar um numero inteiro para o 28379D")
                print("2. Receber um numero inteiro do 28379D")
                print("3. Enviar um vetor de inteiros")
                print("4. Receber um vetor de inteiros")
                print("0. Sair")
                
                choice = input("Escolha uma opcao: ")

                if choice == '1':
                    send_int(ser)

                elif choice == '2':
                    receive_int(ser)

                elif choice =='3':
                    send_vect(ser)

                elif choice =='4':
                    receive_vect(ser)

                elif choice == '0':
                    print("Encerrando o programa.")
                    break
                else:
                    print("Opcao invalida. Tente novamente.")

    except serial.SerialException as e:
        print(f"\nERRO: Nao foi possivel abrir a porta serial '{SERIAL_PORT}'.")
        print(f"Detalhe: {e}")
        print("Verifique se a porta esta correta e se nenhum outro programa a esta usando.")

def send_int(ser_connection):
    """
    Pede um numero ao usuario, o empacota e envia para o microcontrolador.
    """
    try:
        num_str = input("Digite um numero inteiro para ENVIAR (entre -32768 e 32767): ") 
        number_to_send = int(num_str)
        print(f"tamanho do numero: {number_to_send.bit_length()}")
        if not -32768 <= number_to_send <= 32767:
            print("ERRO: O numero esta fora do range permit3ido para um int16_t.")
            return

        # Empacota o COMANDO e o DADO em uma sequencia de bytes.
        # Formato: '<' (Little-endian), 'B' (byte, para o comando), 'h' (short, para o int16), 'h' para o tamanho do dado.
        packet_to_send = struct.pack('<Bhh', CMD_RECEIVE_INT, 2, number_to_send)
        
        print(f"\nEnviando pacote de {len(packet_to_send)} bytes: {packet_to_send.hex(' ')}")
        ser_connection.write(packet_to_send)
        print("Pacote enviado com sucesso.")

    except ValueError:
        print("ERRO: Entrada invalida. Por favor, digite um numero inteiro.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

def send_vect(ser_connection):
    """
    Gera um vetor de sinal e envia para o microcontrolador.
    """
    try:
        #vetor = gerar_sinal()
        #vetor = gerar_sinal_200hz()
        #vetor = gerar_sinal_com_ciclos()
        vetor = gerar_sinal_com_harmonicas()
        tamanho_bytes = len(vetor) * 2  # Cada int16 ocupa 2 bytes

        # Header: comando + tamanho do payload em bytes
        header = struct.pack('<Bh', CMD_RECEIVE_INT, tamanho_bytes)

        # Payload: vetor de Tam_vect inteiros de 16 bits Tam_vect 
        payload = struct.pack(f'<{len(vetor)}h', *vetor)

        packet_to_send = header + payload

        print(f"\nEnviando vetor com {len(vetor)} valores (total: {len(packet_to_send)} bytes)")
        ser_connection.write(packet_to_send)
        print("Vetor enviado com sucesso.")

    except Exception as e:
        print(f"Ocorreu um erro inesperado ao enviar vetor: {e}")


def receive_int(ser_connection):
    """
    Envia um comando para o microcontrolador solicitando um dado e depois o recebe.
    """
    try:
        # 1. Envia apenas o COMANDO para solicitar o dado.
        #    O pacote tera 3 bytes.
        request_packet = struct.pack('<Bh', CMD_SEND_INT, 0)

        print(f"\nEnviando comando de solicitacao (1 byte): {request_packet.hex(' ')}")
        ser_connection.write(request_packet)

        # 2. Aguarda a resposta do microcontrolador.
        #    O 28379D deve responder enviando apenas o dado (int16_t = 2 bytes).
        print("Aguardando resposta do 28379D...")
        response_data = ser_connection.read(2)
        ser_connection.flushInput()  # Limpa o buffer de entrada

        if not response_data or len(response_data) < 2:
            print("ERRO: Nao houve resposta do microcontrolador (timeout).")
            return

        # 3. Desempacota os bytes recebidos para um inteiro.
        #    Formato: '<' (Little-endian), 'h' (short, para o int16)
        received_number = struct.unpack('<h', response_data)[0]

        print(f"  -> Numero recebido do 28379D: {received_number}, tamanho em bits do num: {received_number.bit_length()}")

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

def receive_vect(ser_connection):
    try:
        # 1. Cria o pacote de comando:
        #    - '<'  → little-endian
        #    - 'B'  → 1 byte para o comando (CMD_SEND_INT)
        #    - 'h'  → 2 bytes para o tamanho dos dados (0 nesse caso)
        #    O pacote resultante tem 3 bytes: [comando, 0x00, 0x00]
        request_packet = struct.pack('<Bh', CMD_SEND_INT, 0)

        # Envia o pacote pela porta serial para o microcontrolador
        ser_connection.write(request_packet)

        # 2. Aguarda a resposta: Tam_vect inteiros de 16 bits (int16_t), ou seja, 1024 bytes
        response_data = ser_connection.read(2 * 500)

        # Limpa qualquer lixo que sobrou no buffer da serial
        ser_connection.flushInput()

        # Verifica se recebeu todos os dados esperados
        if len(response_data) < 2 * 500:
            print("Erro: Dados incompletos recebidos.")
            return []
        
        # 3. Converte os 1024 bytes recebidos em Tam_vect inteiros com sinal (int16)
        #    - '<Tam_vecth' → little-endian, Tam_vect valores do tipo short (int16_t)
        received_number = list(struct.unpack('<500h', response_data))
        # 4. Plota o vetor recebido como uma curva (útil para sinais)
        plt.plot(received_number)
        plt.title("Vetor Recebido do 28379D")
        plt.xlabel("Índice")
        plt.ylabel("Valor")
        plt.grid(True)
        plt.show()
        calcular_fft(received_number, amostragemADC)

        # 5. Retorna o vetor convertido para uso no restante do programa

        return received_number

    except Exception as e:
        # Captura e exibe qualquer erro ocorrido durante a execução
        print("Erro ao receber vetor:", e)
        return []
    except Exception as e:
        print("Erro ao receber vetor:", e)
        return []
  
def calcular_fft(sinal, f_amostragem):
    N = len(sinal)
    sinal = sinal - np.mean(sinal)
    fft_resultado = np.fft.fft(sinal)  # Mantém a componente DC original
    fft_magnitude = np.abs(fft_resultado) / N  # Normalização clássica
    fft_magnitude = fft_magnitude[:N // 2] * 2  # Espectro unilateral (exceto DC)
    fft_magnitude[0] = fft_magnitude[0] / 2  # Corrige a magnitude do bin DC (opcional)
    
    frequencias = np.fft.fftfreq(N, d=1/f_amostragem)[:N // 2]
    
    # Plot com stem (barras verticais)
    plt.figure(figsize=(10, 4))
    plt.stem(frequencias, fft_magnitude, markerfmt='C0o', linefmt='C0-', basefmt='C7-')
    plt.title("FFT do Sinal (com componente DC)")
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("Magnitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return frequencias, fft_magnitude

def calcular_alias(f_original, f_amostragem):
    f_nyquist = f_amostragem / 2
    n = round(f_original / f_amostragem)
    print( "componente com alias",abs(f_original - n * f_amostragem))

if __name__ == "__main__":
    main()

