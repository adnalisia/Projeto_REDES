import socket
import threading
from datetime import datetime
from pathlib import Path
import random
import functions
import queue

class UDPClient:  # criando a classe do cliente

    def __init__(self, host, port):
        self.hostaddress = (host , port)
        self.nickname = None  # nome do cliente
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)# criando um socket udp
        self.client_IP = None # endereço ip do cliente
        self.client_port = None # porta do cliente  
        self.seqnumber = 0 # ultimo seqnumber recebido
        self.ackflag = False # flag pra indicar se o ack foi recebido
        self.ackok = False # flag pra indicar se a mensagem recebida não foi corrompida
        self.messagequeue = '' # fila da mensagem recebida antes de ser printada
        self.synack = False # flag pra indicar se recebeu synack
        self.connected = False # flag pra indicar se o a conexão foi feita
        self.lastseqnumber = 0 # ultimo seqnumber enviado
        self.msgrcv = queue.Queue()

    def start(self):
        # pedindo o comando inicial
        starter_input = input(
            "Para se conectar ao chat digite 'hi, meu nome eh' e seu username.\nPara sair do chat digite 'bye'.\n")
        checking_substring = starter_input[0:15]
        # é feita uma checagem para garantir que se o comando inicial não estiver nesse formato, a conexão não inicia
        if checking_substring == "hi, meu nome eh":
            # se ta no formato certo, chama o threeway handshake
            self.threeway_handshake(starter_input)
            # crio o apelido da pessoa
            self.nickname = starter_input[16:] 
            # agora se tiver conectado certo chama a thread de receber mensagens:
            if self.connected:                
                thread3 = threading.Thread(target=self.rcvmessages)
                thread3.start()
                thread2 = threading.Thread(target=self.rcvmsgtreat)
                thread2.start()
            # enquanto estiver conectado, pede os inputs
            while self.connected:
                # tenta receber um input
                try:
                    message = input("(Para sair do chat digite 'bye'): ")
                    #manda a mensagem pra fragmentação
                    self.message_treatment(message)  
                # se não receber um input faz nada
                except:
                    pass

        else:
            # caso a mensagem inicial esteja errada
            print(
                "ERRO: Por favor envie a mensagem inicial com seu nome para ser conectado ao chat.")
            # chama a função inicial de novo
            self.start()


    # função do threeway handshake
    def threeway_handshake(self, hello_message):
        # cria o pacote e envia a mensagem de iniciar	        
        sndpkt = functions.make_pkt(hello_message, self.seqnumber)
        self.socket.sendto(sndpkt.encode(), self.hostaddress)
        # começa o timer
        self.socket.settimeout(1)
        # tenta receber o synack
        try:
            # enquanto não receber o synack
            while not self.connected:
                rcvpkt = self.socket.recv(1024)
                message, _, state = functions.open_pkt(rcvpkt.decode())
                # checa se a mensagem é ack ou synack
                if state == 'ACK' and message == 'SYNACK':
                    # se for muda a flag do connected pra fechar o loop
                    self.connected = True
                    # recebe o ip e a porta do cliente
                    self.client_IP, self.client_port = self.socket.getsockname()
                # se não for synack ou se tiver corrompido
                else:
                    # chama a threeway pra tentar conexão de novo
                    self.threeway_handshake(hello_message)
        # se der timeout tenta estabelecer a conexão de novo
        except socket.timeout:
            self.threeway_handshake(hello_message)

    # função para tratar as mensagens seguintes:
    def message_treatment(self, initial_message):
        # variável com o tempo e a hora exata
        now = datetime.now()
        # cria um timestamp pra ser usado no cabeçalho da mensagem e no titulo dos arquivos fragmentados
        timestamp = f"{now.hour}:{now.minute}:{now.second} {now.day}/{now.month}/{now.year}"
        # bota cabeçalho
        segment = f"{self.client_IP}:{self.client_port}/~{self.nickname}: {initial_message} {timestamp}"
        # chama a função pra fragmentar
        self.message_fragment(segment)


    # função para lidar com as mensagens
    def rcvmessages(self):
        # enquanto estiver conectado
        while self.connected:
            try:
                # chama a mensagem
                rcvpkt = self.socket.recv(1024)
                # recebe a mensagem, seu numero de sequencia e estado
                message, seqnumb, state = functions.open_pkt(rcvpkt.decode())
                self.msgrcv.put((message, seqnumb, state))
            except:
                pass
    
    def rcvmsgtreat(self):
        while self.connected:
            try:
                message, seqnumb, state = self.msgrcv.get()
                if message == 'ACK':
                    # se a msg não tiver corrompida
                    if state == 'ACK':
                        self.ackok = True # muda a flag pra avisar que não esta corrompido
                        self.ackflag = True # muda a flag pra avisar que o ack foi recebido
                # se a mensagem for um NAK
                elif message == 'NAK':
                    # se a msg não tiver corrompida
                    if state == 'ACK':
                        self.ackflag = True # muda a flag pra avisar que o ack/nak foi recebido
                # se a mensagem for um finak e ai encerra a conexão
                elif message == 'FINACK':
                    # se a msg não tiver corrompida
                    if state == 'ACK':
                        self.ackflag = True # muda a flag pra avisar que um ack/nak foi recebido
                        self.connected = False # fecha a conexão
                # se a msg for qualquer outra
                else:
                    if state == 'ACK': #se ela não tiver corrompida
                        if seqnumb != self.lastseqnumber: # se não for repetida
                            self.message_defrag(message) # manda a msg recebida pra desfragmentação
                            self.sndack('ACK', seqnumb) # manda o ack da mensagem
                            self.lastseqnumber = seqnumb # atualiza o ultimo seqnumber recebido
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
        # envia arquivos para o servidor
        sndpkt = functions.make_pkt(data, self.seqnumber)
        self.socket.sendto(sndpkt.encode(), self.hostaddress)
        self.socket.settimeout(0.01)
        # coloca ambas as flags pra negativo
        self.ackflag = False
        self.ackok = False
        # tenta receber o ack
        try:
            #chama a função de esperar ack
            flag = self.waitack()
            #se for um nak recebido reenvia o pacote
            if not flag:
                self.sndpkt(data)
        #caso dê timeout reenvia o pacote
        except socket.timeout:
            print('SOCKET TIMEOUT')
            self.sndpkt(data)
    
    # função para enviar ack
    def sndack(self, data, seqnumb):
        # envia ack para o servirdor
        sndpkt = functions.make_pkt(data, seqnumb)
        self.socket.sendto(sndpkt.encode(), self.hostaddress)

    # função para esperar o ack
    def waitack(self):
        # espera receber ack
        while not self.ackflag:
            self.ackflag = False
        # se o for um ack, retorna verdadeiro
        if self.ackok:
            return True
        # se for um nak retorna falso
        else:
            return False

# inicia o chat
if __name__ == "__main__":
    client = UDPClient("localhost", 50000)
    client.start()