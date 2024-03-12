import socket
import threading
from datetime import datetime
from pathlib import Path
import random
import functions

class UDPClient:  # criando a classe do cliente

    def __init__(self, host, port):
        self.hostaddress = (host , port)
        self.nickname = None  # nome do cliente
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)# criando um socket udp
        self.client_IP = None
        self.client_port = None # endereço do cliente  
        self.seqnumber = 0
        self.lastack = 0
        self.ackflag = False
        self.ackok = False
        self.messagequeue = ''
        self.synack = False
        self.connected = False
        self.lastseqnumber = 1

    def start(self):
        # primeiro cria-se um while para receber o input que conecta ao servidor
            # pedindo o comando inicial
            starter_input = input(
                "Para se conectar ao chat digite 'hi, meu nome eh' e seu username.\nPara sair do chat digite 'bye'.\n")
            checking_substring = starter_input[0:15]
            # é feita uma checagem para garantir que se o comando inicial não estiver nesse formato, a conexão não inicia
            if checking_substring == "hi, meu nome eh":
                self.threeway_handshake(starter_input)
                self.nickname = starter_input[16:] 
                # chama a função para o threeway handshake:
                if self.connected:
                    thread3 = threading.Thread(target=self.rcvmessages)
                    thread3.start()
                # aqui ele corta o input inicial para pegar apenas o nome do usuário e aplicar
                while self.connected:
                    try:
                        message = input("(Para sair do chat digite 'bye'): ")
                        self.message_fragment(message)  
                    except:
                        pass
 
            else:
                print(
                    "ERRO: Por favor envie a mensagem inicial com seu nome para ser conectado ao chat.")
                self.start()


    # função do threeway handshake
    def threeway_handshake(self, hello_message):
        #envia a mensagem de iniciar	        
        sndpkt = functions.make_pkt(hello_message, self.seqnumber)
        self.socket.sendto(sndpkt.encode(), self.hostaddress)
        #começa o timer
        self.socket.settimeout(1)
        try:
            while not self.synack:
                rcvpkt = self.socket.recv(1024)
                message, _, state = functions.open_pkt(rcvpkt.decode())
                if state == 'ACK' and message == 'SYNACK':
                    self.synack = True
                    self.connected = True
                    self.seqnumber = 1
                    self.client_IP, self.client_IP = self.socket.getsockname()
                #se não for synack ou se tiver corrompido
                else:
                    self.threeway_handshake(hello_message)
        #se der timeout tenta estabelecer a conexão de novo
        except socket.timeout:
            self.threeway_handshake(hello_message)

    # função para tratar as mensagens seguintes:
    def message_treatment(self, initial_message):
        # variável com o tempo e a hora exata
        now = datetime.now()
        # cria um timestamp pra ser usado no cabeçalho da mensagem e no titulo dos arquivos fragmentados
        timestamp = f"{now.hour}:{now.minute}:{now.second} {now.day}/{now.month}/{now.year}"
        #bota cabeçalho
        segment = f"{self.client_IP}:{self.client_port}/~{self.nickname}: {initial_message} {timestamp}"
        #chama a função pra fragmentar
        self.message_fragment(segment)


    #função para lidar com as mensagens
    def rcvmessages(self):
        while self.connected:
            try:
                #chama a mensagem
                rcvpkt = self.socket.recv(1024)
                #recebe a mensagem, seu numero de sequencia e estado
                message, seqnumb, state = functions.open_pkt(rcvpkt.decode())            
                #se a mensagem for um ack
                if message == 'ACK':
                    if state == 'ACK':
                        self.lastack = seqnumb
                        self.ackok = True
                        self.ackflag = True
                #se a mensagem for um NAK
                elif message == 'NAK':
                    if state == 'ACK':
                        self.ackflag = True
                        self.ackok = False
                #se a mensagem for um finak e ai encerra a conexão
                elif message == 'FINAK':
                    if state == 'ACK':
                        self.ackflag = True
                        self.connected = False
                else:
                    if state == 'ACK':
                        if seqnumb != self.lastseqnumber:
                            if self.connected:
                                self.message_defrag(message)
                                self.sndack('ACK', seqnumb)
                                self.lastseqnumber = seqnumb
                    #se a mensagem tiver corrompida, envia um NAK para o cliente
                    else:
                        self.sndack('NAK', seqnumb)
            except:
                pass


    # modulo que fragmenta mensagens
    def message_fragment(self, segment):
        # cria um número aleatório para criação de arquivo
        file_name = random.randint(0, 10000)
        # cria um arquivo .txt para a mensagem
        with open(f'{file_name}', 'w') as file:
            # escreve mensagem no arquivo
            file.write(f"{segment}")
            file.close()

        # verifica o tamanho do arquivo
        size = Path(f'{file_name}').stat().st_size
        # condição para arquivos maiores que 1kb
        if size > 1024:
            # cria um arquivo .txt
            with open(f'{file_name}', 'r') as file:
                # lê 1kb do arquivo
                kbyte = file.read(1024)
                # loop que cria vários arquivos com 1024 bytes no máximo
                while kbyte:
                    #envia o pacote
                    self.sndpkt(kbyte)
                    #lê o próximo kbyte
                    kbyte = file.read(1024)

            # envia mensagem de finalização para o servidor
            self.sndpkt('finish')

        else:
            # envia arquivo pro servidor
            self.sndpkt(segment)
            # envia mensagem de finalização para o servidor
            self.sndpkt('finish')

    # modulo recursivo que reconstroi mensagens
    def message_defrag(self, message):
        # Se a mensagem atual contém 'finish'
        if 'finish' == message:
            #printa a mensagem
            print (self.messagequeue)
            #limpa a fila
            self.messagequeue = ''
        #se não for, adiciona a mensagem a fila
        else:
            self.messagequeue += message              

    #função de enviar
    def sndpkt(self, data):
        self.seqnumber = (self.seqnumber + 1)%2
        # envia arquivos para o servirdor
        sndpkt = functions.make_pkt(data, self.seqnumber)
        self.socket.sendto(sndpkt.encode(), self.hostaddress)
        self.socket.settimeout(0.01)
        self.ackflag = False
        self.ackok = False
        #tentar receber o ack
        try:
            flag = self.waitack()
            if not flag:
                self.sndpkt(data)
        #caso dê timeout
        except socket.timeout:
            print('SOCKET TIMEOUT')
            self.sndpkt(data)
    
    def sndack(self, data, seqnumb):
        # envia ack para o servirdor
        sndpkt = functions.make_pkt(data, seqnumb)
        self.socket.sendto(sndpkt.encode(), self.hostaddress)

    #função para esperar o ack
    def waitack(self):
        #espera receber ack
        while not self.ackflag:
            self.ackflag = False
        if self.ackok:
            return True
        else:
            return False



# inicia o chat
if __name__ == "__main__":
    client = UDPClient("localhost", 50000)
    client.start()