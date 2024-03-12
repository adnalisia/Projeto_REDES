import socket
import threading
from datetime import datetime
from pathlib import Path
import random
import time
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
        self.ack = threading.Condition()
        self.ackflag = False
        self.ackok = False
        self.messagequeue = ''
        self.synack = False
        self.connected = False

    def start(self):
        # primeiro cria-se um while para receber o input que conecta ao servidor
        while True:
            # pedindo o comando inicial
            starter_input = input(
                "Digite 'hi, meu nome eh' e seu nome para se conectar ao chat:")
            checking_substring = starter_input[0:15]
            # é feita uma checagem para garantir que se o comando inicial não estiver nesse formato, a conexão não inicia
            if checking_substring == "hi, meu nome eh":
                # chama a função para o threeway handshake:
                self.threeway_handshake(starter_input)
                # aqui ele corta o input inicial para pegar apenas o nome do usuário e aplicar
                self.nickname = starter_input[16:]
                while self.connected:
                    message = input()
                    self.message_fragment(message)    
            else:
                print(
                    "ERRO: Por favor envie a mensagem inicial com seu nome para ser conectado ao chat.")


    # função do threeway handshake
    def threeway_handshake(self, hello_message):
        #envia a mensagem de iniciar	        
        self.sndpkt('connected')
        self.threads_rcv()
        #começa o timer
        self.socket.settimeout(1.0)
        try:
            with self.ack:
                while not self.ackflag:
                    self.ack.wait()
            #recebeu o pacote, agora checa se ta corrompido
            if self.ackok:
                #checa se não é o synack
                if not self.synack:
                    #se não for, tenta estabelecer a conexão de novo
                    self.threeway_handshake(hello_message)
                else:
                    #se for cria a thread
                    self.connected = True
                    self.message_fragment(hello_message)
                    return self.socket
            #se ta corrompido, envia msg de conexão de novo
            else:
                self.threeway_handshake(hello_message)
        #se der timeout tenta estabelecer a conexão de novo
        except socket.timeout:
            self.threeway_handshake(hello_message)

    # função para o cliente receber threads:
    def threads_rcv(self):
        thread1 = threading.Thread(target=self.waitack())
        thread2 = threading.Thread(target=self.rcvmessages())
        thread3 = threading.Thread(target=self.start())
        thread3.start()
        thread1.start()
        thread2.start()

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
        while True:
            #chama a mensagem
            rcvpkt = self.socket.recv(1024)
            #recebe a mensagem, seu numero de sequencia e estado
            message, seqnumb, state = functions.open_pkt(rcvpkt.decode())
            #vê se a mensagem não ta corrompida
            if 
            
            #se a mensagem for um ack
            if message == 'ACK':
                if state == 'ACK':
                    self.lastack = seqnumb
                    self.ackok = True
                    with self.ack:
                        self.ackflag = True
                        self.ack.notify()
            #se a mensagem for um synack
            elif message == 'SYNACK':
                if state == 'ACK':
                    self.lastack = seqnumb
                    self.connected = True
                    self.ackok = True
                    with self.ack:
                        self.ackflag = True
                        self.synack = True
                        self.ack.notify()
            #se a mensagem for um NAK
            elif message == 'NAK':
                if state == 'ACK':
                    with self.ack:
                        self.ackflag = True
                        self.ack.notify()
            #se a mensagem for um finak e ai encerra a conexão
            elif message == 'FINAK':
                if state == 'ACK':
                    self.connected = False
                    with self.ack:
                        self.ackflag = True
                        self.ack.notify()
                    self.socket.close()
            else:
                if state == 'ACK':
                    if seqnumb != self.seqnumber:
                        if message.startswith('IP.PORT'):
                            rcvpkt = message.split(',')
                            address = rcvpkt.split('/')
                            self.client_IP = address[0]
                            self.client_port = address[1]
                            self.socket.bind(self.myaddress)
                        #se a mensagem for qualquer outra
                        elif self.connected:
                            self.message_defrag(message)
                            self.sndack('ACK', seqnumb)
                #se a mensagem tiver corrompida, envia um NAK para o cliente
                else:
                    self.sndack('NAK', seqnumb)
    


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
                    #altera o seqnumber da mensagem
                    self.seqnumber = (self.seqnumber + 1) //2
                    #envia o pacote
                    self.sndpkt(kbyte)
                    #lê o próximo kbyte
                    kbyte = file.read(1024)

            # envia mensagem de finalização para o servidor
            self.sndpkt('finish')

        else:
            #altera o seqnumber da mensagem
            self.seqnumber = (self.seqnumber + 1) //2
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
        # envia arquivos para o servirdor
        sndpkt = functions.make_pkt(data, self.seqnumber)
        self.socket.sendto(sndpkt.encode(), self.hostaddress)
        self.socket.settimeout(0.01)
        self.ackok = False
        #tentar receber o ack
        try:
            flag = self.waitack()
            if not flag:
                self.sndpkt(data)
        #caso dê timeout
        except socket.timeout:
            self.sndpkt(data)
    
    def sndack(self, data, seqnumb):
        # envia arquivos para o servirdor
        sndpkt = functions.make_pkt(data, seqnumb)
        self.socket.sendto(sndpkt.encode(), self.hostaddress)

    #função para esperar o ack
    def waitack(self):
        with self.ack:
            #enquanto a flag de que recebeu ack não for verdade
            while self.ackflag:
                #espera receber ack
                self.ack.wait()
            #se for um NAK reenvia os dados
            if not self.ackok:
                return False
            else:
                return True

# inicia o chat
if __name__ == "__main__":
    client = UDPClient("localhost", 50000)
    client.start()