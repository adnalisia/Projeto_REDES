import socket
import threading
from datetime import datetime
from pathlib import Path
import random
import os


class UDPClient: #criando a classe do cliente

    def __init__(self, host, port):
        self.host = host #host do servidor
        self.port = port #porta do servidor
        self.client_IP = "localhost" #ip do cliente
        self.client_port = 4455 #servidor do cliente
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
        self.message_treatment(starter_input)

    #função que avisa o servidor que um novo cliente se conectou
    def exchange_info(self, hello_message):
        self.socket.sendto(hello_message.encode(), (self.host, self.port))

    #função para conectar o cliente ao chat de mensagens:
    def connect_thread(self):
        thread = threading.Thread(target=self.receive_messages)
        thread.start()

    #função para tratar as mensagens seguintes:
    def message_treatment(self,initial_message):
        #variável com o tempo e a hora exata
        now = datetime.now() 
        #cria um timestamp pra ser usado no cabeçalho da mensagem e no titulo dos arquivos fragmentados
        timestamp = f"{now.hour}:{now.minute}:{now.second} {now.day}/{now.month}/{now.year}"
        segment = f"{self.client_IP}:{self.client_port}/~{self.nickname}: {initial_message} {timestamp}"
        self.message_fragment(segment)
        #um loop que depende da flag de conexão
        while self.connection_flag: 
            message = input()
            #variável com o tempo e a hora exata
            now = datetime.now() 
            #cria um timestamp pra ser usado no cabeçalho da mensagem e no titulo dos arquivos fragmentados
            timestamp = f"{now.hour}:{now.minute}:{now.second} {now.day}/{now.month}/{now.year}"  
            #checkagem para fechar o loop
            if message == "bye": 
                self.socket.sendto(message.encode(), (self.host, self.port))
                self.connection_flag = False
            #aqui coloca o cabeçalho nas mensagens
            else: 
                segment = f"{self.client_IP}:{self.client_port}/~{self.nickname}: {message} {timestamp}"
                #chama a função para fragmentar as mensagens e mandar pro servidor
                self.message_fragment(segment) 

    #função para receber mensagens do servidor
    def receive_messages(self): 
        try:
            data, _ = self.socket.recvfrom(self.buffer_size)
            #a primeira mensagem que ele recebe é o IP e a Porta do cliente
            client_id = data.decode().split('/') 
            #atualiza ip
            self.client_IP = client_id[0] 
            #atualiza porta
            self.client_port = client_id[1] 
            
            #loop que depende também da flag de conexão
            while self.connection_flag: 
                data, _ = self.socket.recvfrom(self.buffer_size)
                #manda a mensagem pro modulo de reconstrução
                message = self.message_defrag('',data) 
                #printa a mensagem na tela
                print(message) 

        except Exception as e:
            print(f"Error in receive_messages: {e}")

    #modulo que fragmenta mensagens     
    def message_fragment(self, segment):
        file_name = random.randint(0, 10000)
        #cria um arquivo .txt para a mensagem
        file = open(f'{file_name}', 'w')
        file.write(f"{segment}")
        file.close()
            
        #verifica o tamanho do arquivo
        size = Path(f'{file_name}').stat().st_size
        #fragmenta arquivo maior que 1024 bytes
        if size > 1024:
            slice = 0
            with open(f'{file_name}', 'r') as file:
                kbyte = file.read(1024)
                #loop que cria vários arquivos com 1024 bytes no máximo
                while kbyte:
                    new_file = f"{file_name}{str(slice)}.txt"
                    frag_file = open(new_file, 'w')
                    frag_file.write(kbyte)
                    frag_file.close()

                    self.socket.sendto(new_file, (self.host, self.port))
                    new_file.unlink()
                
                    kbyte = file.read(1024)
                    slice += 1
                #envia arquivo pro servidor
                ###incluir classe e modulo do server###
                
            #informa o termino de envio da mensagem
            text = open("end_file.txt", 'w')
            text.write("finish")
            text.close()
            ###incluir classe e modulo do server###
            self.socket.sendto(text, (self.host, self.port))
            text.unlink()
            
        else:
            #envia arquivo pro servidor
            self.socket.sendto(file, (self.host, self.port))
            ###incluir classe e modulo do server###
            
            #informa o termino de envio da mensagem
            text = open("end_file.txt", 'w')
            text.write("finish")
            text.close()
            ###incluir classe e modulo do server###

            self.socket.sendto(text, (self.host, self.port))
            text.unlink()
            

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
            message.unlink()
            data, _ = self.socket.recvfrom(self.buffer_size)
            self.message_defrag(text, data)

#inicia o chat
if __name__ == "__main__":
    client = UDPClient("localhost", 50000)
    client.start()