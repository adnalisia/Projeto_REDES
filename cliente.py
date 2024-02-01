import socket
import threading
from datetime import datetime
from pathlib import Path


class UDPClient: #criando a classe do cliente

    def __init__(self, host, port):
        self.host = host #host do servidor
        self.port = port #porta do servidor
        self.client_IP = None #ip do cliente
        self.client_port = None #servidor do cliente
        self.nickname = None #nome do cliente
        self.connection_flag =  False #flag que indica se a conexão esta aberta
        self.buffer_size = 1024 #tamanho do meu buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #criando um socket udp

    def start(self):
        #primeiro cria-se um while para receber o input que conecta ao servidor
        while not self.connection_flag:
            #pedindo o comando inicial
            starter_input = input("Digite 'hi, meu nome eh' e seu nome para se conectar ao chat:")
            checking_substring = starter_input[0:15]
            #é feita uma checagem para garantir que se o comando inicial não estiver nesse formato, a conexão não inicia
            if checking_substring == "hi, meu nome eh":
                self.connection_flag = True
                self.nickname = starter_input[16:] #aqui ele corta o input inicial para pegar apenas o nome do usuário e aplicar
            else:
                print("ERRO: Por favor envie a mensagem inicial com seu nome para ser conectado ao chat.")
        #enviar informações do usuário pro servidor:
        self.exchange_info(starter_input)
        #conectando o cliente ao chat de mensagens:
        self.connect_thread()
        #chamando a função de tratamento de mensagens:
        self.message_treatment()

    #função que avisa o servidor que um novo cliente se conectou
    def exchange_info(self, hello_message):
        self.socket.sendto(hello_message.encode(), (self.host, self.port))

    #função para conectar o cliente ao chat de mensagens:
    def connect_thread(self):
        thread = threading.Thread(target=self.receive_messages)
        thread.start()

    #função para tratar as mensagens seguintes:
    def message_treatment(self):
        #um loop que depende da flag de conexão
        while self.connection_flag: 
            message = input()
            #variável com o tempo e a hora exata
            now = datetime.now() 
            #cria um timestamp pra ser usado no cabeçalho da mensagem e no titulo dos arquivos fragmentados
            timestamp = f"{now.hour}:{now.minute}:{now.second} {now.day}/{now.month}/{now.year}"  
            if message == "bye": #checkagem para fechar o loop
                self.socket.sendto(message.encode(), (self.host, self.port))
                self.connection_flag = False
            else: #aqui coloca o cabeçalho nas mensagens
                segment = f"{self.client_IP}:{self.client_port}/~{self.nickname}: {message} {timestamp}"
                self.message_fragment(segment, timestamp) #chama a função para fragmentar as mensagens e mandar pro servidor

    def receive_messages(self): #função para receber mensagens do servidor
        data, _ = self.socket.recvfrom(self.buffer_size)
        client_id = data.decode().split('/') #a primeira mensagem que ele recebe é o IP e a Porta do cliente
        self.client_IP = client_id[0] #atualiza ip
        self.client_port = client_id[1] #atualiza porta

        while self.connection_flag: #loop que depende também da flag de conexão
            data, _ = self.socket.recvfrom(self.buffer_size)
            message = self.message_defrag(data.decode()) #manda a mensagem pro modulo de reconstrução
            print(message) #printa a mensagem na tela
     
    #modulo que fragmenta mensagens     
    def message_fragment(segment, timestamp):
        #cria um arquivo .txt para a mensagem
        with open(f'{timestamp}', 'w') as file:
            file.write(f"{segment}")
            file.close()
            
        #verifica o tamanho do arquivo
        size = Path(file).stat().st_size
        #fragmenta arquivo maior que 1024 bytes
        if size > 1024:
            slice = 0
            kbyte = file.read(1024)
            #loop que cria vários arquivos com 1024 bytes no máximo
            while kbyte:
                new_file = f"{timestamp}{str(slice)}.txt"
                frag_file = open(new_file, 'w')
                frag_file.write(kbyte)
                frag_file.close()

                kbyte = file.read(1024)
                slice += 1
                #envia arquivo pro servidor
                ###incluir classe e modulo do server###
                
            #informa o termino de envio da mensagem
            text = open("end_file.txt", 'w')
            text.write("finish")
            text.close()
            ###incluir classe e modulo do server###
            
        else:
            #envia arquivo pro servidor
            ###incluir classe e modulo do server###
            
            #informa o termino de envio da mensagem
            text = open("end_file.txt", 'w')
            text.write("finish")
            text.close()
            ###incluir classe e modulo do server###
    
    #modulo que reconstroi mensagens
    def message_defrag(message):
        text = message.read()
        if text == "finish":
            pass
        else:  
            return text

if __name__ == "__main__":
    client = UDPClient("localhost", 50000)
    client.start()
