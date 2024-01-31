import socket
import threading
from datetime import datetime

class UDPClient: #criando a classe do cliente

    def __init__(self, host, port):
        self.host = host #host do servidor
        self.port = port #porta do servidor
        self.client_IP = None #ip do cliente
        self.client_port = None #servidor do cliente
        self.nickname = None #nome do cliente
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #criando um socket udp
    
    def start(self):
        #primeiro cria-se um while para receber o input que conecta ao servidor
        connection_flag = True
        while connection_flag:
            #pedindo o comando inicial
            starter_input = input("Digite 'hi, meu nome eh' e seu nome para se conectar ao chat:")
            checking_substring = starter_input[0:15]
            #é feita uma checagem para garantir que se o comando inicial não estiver nesse formato, a conexão não inicia
            if checking_substring == "hi, meu nome eh":
                connection_flag = False
                self.nickname = starter_input[16:] #aqui ele corta o input inicial para pegar apenas o nome do usuário e aplicar
            else:
                print("ERRO: Por favor envie a mensagem inicial com seu nome para ser conectado ao chat.")
        #enviar informações do usuário pro servidor:
        self.exchange_info()
        #conectando o cliente ao chat de mensagens:
        self.connect_thread()
        #chamando a função de tratamento de mensagens:
        self.message_treatment()
    
    #função trocar informações do cliente para o servidor
    def exchange_info(self):
        self.socket.sendto(self.nickname.encode(), (self.host, self.port))
        r
    
    #função para conectar o cliente ao chat de mensagens:
    def connect_thread(self):
        thread = threading.Thread(target=self.receive_messages)
        thread.start()
    
    #função para tratar as mensagens seguintes:
    def message_treatment(self):
        connection_flag = True
        while connection_flag:
            message = input()
            timestamp = f"{now.hour}:{now.minute}:{now.second} {now.day}/{now.month}/{now.year}"
            if message == "bye":
                self.socket.sendto(message.encode(), (self.host, self.port))
                connection_flag = False
            else:
                segment = f"{self.client_IP}:{self.client_port}/~{self.nickname}: {message} {timestamp}"
                self.message_fragment(segment)
    
    

        
