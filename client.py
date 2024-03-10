import socket
import threading
from datetime import datetime
from pathlib import Path
import random
import time
import functions


class UDPClient:  # criando a classe do cliente

    def __init__(self, host, port):
        self.host = host  # host do servidor
        self.port = port  # porta do servidor
        self.client_IP = None # ip do cliente
        self.client_port = None  # porta do cliente
        self.nickname = None  # nome do cliente
        self.connection_flag = False  # flag que indica se a conexão esta aberta
        self.buffer_size = 1024  # tamanho do meu buffer
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)  # criando um socket udp
        self.seqnumber = 0
        self.seqnmbrcv = 0

    def start(self):
        # primeiro cria-se um while para receber o input que conecta ao servidor
        while not self.connection_flag:
            # pedindo o comando inicial
            starter_input = input(
                "Digite 'hi, meu nome eh' e seu nome para se conectar ao chat:")
            checking_substring = starter_input[0:15]
            # é feita uma checagem para garantir que se o comando inicial não estiver nesse formato, a conexão não inicia
            if checking_substring == "hi, meu nome eh":
                self.connection_flag = True
                # aqui ele corta o input inicial para pegar apenas o nome do usuário e aplicar
                self.nickname = starter_input[16:]
            else:
                print(
                    "ERRO: Por favor envie a mensagem inicial com seu nome para ser conectado ao chat.")
        # chama a função para o threeway handshake:
        self.threeway_handshake(starter_input)
        # chamando a função de tratamento de mensagens:
        self.message_treatment(starter_input)
        #recebe a mensagem do servidor com seu ip:
        self.receive_IP()
        # conectando o cliente ao chat de mensagens:
        self.connect_thread()
    # função do threeway handshake
    def threeway_handshake(self, hello_message):
        #envia a mensagem de iniciar
        functions.rdt_send(hello_message, self.seqnumber, (self.host, self.port))
        #começa o timer
        socket.settimeout(1.0)
        try:
            #tenta receber o pacote
            rcvpkt, _ = self.socket.recvfrom(1024)
            #checa se não é o synack
            if rcvpkt[1].decode() != "SYNACK":
                #se não for, tenta estabelecer a conexão de novo
                self.threeway_handshake(self, hello_message)
        #se der timeout tenta estabelecer a conexão de novo
        except socket.timeout:
            self.threeway_handshake(self, hello_message)

    # função para conectar o cliente ao chat de mensagens:
    def connect_thread(self):
        thread = threading.Thread(target=self.receive_messages)
        thread.start()

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
        # um loop que depende da flag de conexão
        while self.connection_flag:
            message = input()
            # variável com o tempo e a hora exata
            now = datetime.now()
            # cria um timestamp pra ser usado no cabeçalho da mensagem e no titulo dos arquivos fragmentados
            self.start_time = time.time()  # começa a contagem do tempo
            timestamp = f"{now.hour}:{now.minute}:{now.second} {now.day}/{now.month}/{now.year}"
            # aqui coloca o cabeçalho
            segment = f"{self.client_IP}:{self.client_port}/~{self.nickname}: {message} {timestamp}"
            # chama a função para fragmentar as mensagens e mandar pro servidor
            self.message_fragment(segment)

    # função para receber mensagens ip e porta
    def receive_IP(self):
        data, _ = functions.rdt_rcv()
        # a primeira mensagem que ele recebe é o IP e a Porta do cliente
        client_id = data.decode().split('/')
        # atualiza ip
        self.client_IP = client_id[0]
        # atualiza porta
        self.client_port = client_id[1]

    # loop que depende também da flag de conexão
    def receive_messages(self):
        while self.connection_flag:
            #chama a função de enviar o ack
            data, seqnumb = functions.rdt_rcv()
            if seqnumb == 0:
                self.seqnmbrcv = 1
            else:
                self.seqnmbrcv = 0
            # manda a mensagem pro modulo de reconstrução
            message = self.message_defrag('', data.decode(), seqnumb)
            # printa a mensagem na tela
            print(message)

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
                    if self.seqnumber == 0:
                        self.seqnumber = 1
                    else:
                        self.seqnumber = 0
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
    def message_defrag(self, partial_message, message, seqnumb):
        # Se a mensagem atual contém 'finish', retorna a mensagem parcial
        if 'finish' == message:
            return partial_message
        else:
            # Adiciona a mensagem atual à parcial, checando primeiro se não é a mesma mensagem repetida
            if seqnumb != self.seqnmbrcv:
                partial_message += message
                self.seqnmbrcv = seqnumb
            # Caso contrário, continua a receber mensagens e descarta a recebida
            data, seqnumb = functions.rdt_rcv()
            return self.message_defrag(partial_message, data.decode(), seqnumb)

    #função de enviar
    def sndpkt(self, data):
        # envia arquivos para o servirdor
        sndpkt = functions.rdt_send(data, self.seqnumber)
        self.socket.sendto(sndpkt, (self.host, self.port))
        socket.settimeout(1.0)
        #tentar receber o ack
        try:
            infoconf, _ = socket.rcvfrom(self.buffer_size)
            #caso seja corrompido
            if infoconf[1].decode == 'NAK':
                self.sndpkt(data)
            #caso seja encerrando a conversa
            elif infoconf[1].decode == 'FINAK':
                self.connection_flag = False
        #caso seja
        except socket.timeout:
            self.sndpkt(data)

# inicia o chat
if __name__ == "__main__":
    client = UDPClient("localhost", 50000)
    client.start()