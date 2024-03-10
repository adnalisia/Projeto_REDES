import socket
import threading
from datetime import datetime
from pathlib import Path
import random
<<<<<<< HEAD
=======
import time
>>>>>>> 2d2f6cf8b75925e472dbcc0bcccf09d50934c8de


class UDPClient:  # criando a classe do cliente

    def __init__(self, host, port):
        self.host = host  # host do servidor
        self.port = port  # porta do servidor
        self.client_IP = "localhost"  # ip do cliente
        self.client_port = 4455  # servidor do cliente
        self.nickname = None  # nome do cliente
        self.connection_flag = False  # flag que indica se a conexão esta aberta
        self.buffer_size = 1024  # tamanho do meu buffer
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)  # criando um socket udp
        self.socket.settimeout(1.0)  # setando temporizador
        self.start_time = None
        self.end_time = None

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
        # enviar informações do usuário pro servidor:
        self.exchange_info(starter_input)
        # conectando o cliente ao chat de mensagens:
        self.connect_thread()
        # chamando a função de tratamento de mensagens:
        self.message_treatment(starter_input)

    # função que avisa o servidor que um novo cliente se conectou
    def exchange_info(self, hello_message):
        self.socket.sendto(hello_message.encode(), (self.host, self.port))

    # função para conectar o cliente ao chat de mensagens:
    def connect_thread(self):
        thread = threading.Thread(target=self.receive_messages)
        thread.start()

<<<<<<< HEAD
    #função para tratar as mensagens seguintes:
    def message_treatment(self, initial_message):
        #variável com o tempo e a hora exata
        now = datetime.now() 
        #cria um timestamp pra ser usado no cabeçalho da mensagem e no titulo dos arquivos fragmentados
=======
    # função para tratar as mensagens seguintes:
    def message_treatment(self, initial_message):
        # variável com o tempo e a hora exata
        now = datetime.now()
        # cria um timestamp pra ser usado no cabeçalho da mensagem e no titulo dos arquivos fragmentados
>>>>>>> 2d2f6cf8b75925e472dbcc0bcccf09d50934c8de
        timestamp = f"{now.hour}:{now.minute}:{now.second} {now.day}/{now.month}/{now.year}"
        segment = f"{self.client_IP}:{self.client_port}/~{self.nickname}: {initial_message} {timestamp}"
        self.message_fragment(segment)
        # um loop que depende da flag de conexão
        while self.connection_flag:
            message = input()
            # variável com o tempo e a hora exata
            now = datetime.now()
            # cria um timestamp pra ser usado no cabeçalho da mensagem e no titulo dos arquivos fragmentados
            self.start_time = time.time()  # começa a contagem do tempo
            timestamp = f"{now.hour}:{now.minute}:{now.second} {now.day}/{now.month}/{now.year}"
            # checkagem para fechar o loop
            if message == "bye":
                self.socket.sendto(message.encode(), (self.host, self.port))
                self.socket.sendto('finish'.encode(), (self.host, self.port))
                self.connection_flag = False
            # aqui coloca o cabeçalho nas mensagens
            else:
                segment = f"{self.client_IP}:{self.client_port}/~{self.nickname}: {message} {timestamp}"
                # chama a função para fragmentar as mensagens e mandar pro servidor
                self.message_fragment(segment)

    # função para receber mensagens do servidor
    def receive_messages(self):
        try:
            data, _ = self.socket.recvfrom(self.buffer_size)
            # a primeira mensagem que ele recebe é o IP e a Porta do cliente
            client_id = data.decode().split('/')
            # atualiza ip
            self.client_IP = client_id[0]
            # atualiza porta
            self.client_port = client_id[1]

            # loop que depende também da flag de conexão
            while self.connection_flag:
                data, _ = self.socket.recvfrom(self.buffer_size)
<<<<<<< HEAD
                #manda a mensagem pro modulo de reconstrução
                message = self.message_defrag('',data.decode()) 
                #printa a mensagem na tela
                print(message) 
=======
                self.end_time = time.time()  # finaliza a contagem do tempo
                elapsed = self.end_time - self.start_time  # quando tempo gastou
>>>>>>> 2d2f6cf8b75925e472dbcc0bcccf09d50934c8de

                print(f'\n(OK) Mensagem enviada em {elapsed} segundos')
                # manda a mensagem pro modulo de reconstrução
                message = self.message_defrag('', data.decode())
                # printa a mensagem na tela
                print(message[:-6])

        except socket.timeout:
            print('ESGOTADO TEMPO LIMITE')

    # modulo que fragmenta mensagens
    def message_fragment(self, segment):
<<<<<<< HEAD
        #cria um número aleatório para criação de arquivo
        file_name = random.randint(0, 10000)
        #cria um arquivo .txt para a mensagem
        with open(f'{file_name}', 'w') as file:
            #escreve mensagem no arquivo
            file.write(f"{segment}")
            file.close()
            
        #verifica o tamanho do arquivo
        size = Path(f'{file_name}').stat().st_size
        #condição para arquivos maiores que 1kb
        if size > 1024:
            #variável que controla a quantidade de partições
            slice = 0
            #cria um arquivo .txt
            with open(f'{file_name}', 'r') as file:
                #lê 1kb do arquivo
=======
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
>>>>>>> 2d2f6cf8b75925e472dbcc0bcccf09d50934c8de
                kbyte = file.read(1024)
                # loop que cria vários arquivos com 1024 bytes no máximo
                while kbyte:
<<<<<<< HEAD
                    new_file = f"{file_name}{str(slice)}.txt"
                    frag_file = open(new_file, 'w')
                    frag_file.write(kbyte)
                    frag_file.close()
                    #envia arquivos para o servirdor
                    self.socket.sendto(new_file.encode(), (self.host, self.port))
                    #deleta arquivo
                    #new_file.unlink()
                    #lê o proximo kb do arquivo
                    kbyte = file.read(1024)
                    slice += 1
                
            #informa o término de envio da mensagem
            text = open("end_file.txt", 'w')
            text.write("finish")
            text.close()
            #envia o arquivo de término para o servidor
            self.socket.sendto("end_file.txt".encode(), (self.host, self.port))
            #text.unlink()
            
        else:
            #envia arquivo pro servidor
            self.socket.sendto(f'{file}'.encode(), (self.host, self.port))
            #informa o termino de envio da mensagem
            text = open("end_file.txt", 'w')
            text.write("finish")
            text.close()
            #envia arquivo para o servidor
            self.socket.sendto("end_file.txt".encode(), (self.host, self.port))
            #text.unlink()
            
    #modulo recursivo que reconstroi mensagens
    def message_defrag(self, partial_message, message):
        #lê a mensagem recebida
        text = message.read()
        #se a mensagem recebida for finish, retorna a mensagem concatenada até então
        if text == "finish":
            return partial_message
        #se não for, concatena o resto da mensagem, pede a próxima parte da mensagem e chama mais uma vez
        else:
            text = partial_message + text
            #message.unlink()
            #recebe o arquivo do servidor
            data, _ = self.socket.recvfrom(self.buffer_size)
            self.message_defrag(text, data.decode())
=======

                    # envia arquivos para o servirdor
                    self.socket.sendto(kbyte.encode(), (self.host, self.port))

                    # lê o proximo kb do arquivo
                    kbyte = file.read(1024)

            # envia mensagem para o servidor
            self.socket.sendto("finish".encode(), (self.host, self.port))

        else:
            # envia arquivo pro servidor
            self.socket.sendto(segment.encode(), (self.host, self.port))
            # envia mensagem para o servidor
            self.socket.sendto("finish".encode(), (self.host, self.port))

    # modulo recursivo que reconstroi mensagens
    def message_defrag(self, partial_message, message):
        # Adiciona a mensagem atual à parcial
        partial_message += message
>>>>>>> 2d2f6cf8b75925e472dbcc0bcccf09d50934c8de

        # Se a mensagem atual contém 'finish', retorna a mensagem parcial
        if 'finish' in message:
            return partial_message
        else:
            # Caso contrário, continua a receber mensagens
            data, _ = self.socket.recvfrom(self.buffer_size)
            return self.message_defrag(partial_message, data.decode())


# inicia o chat
if __name__ == "__main__":
    client = UDPClient("localhost", 50000)
    client.start()
