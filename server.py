import socket
import threading
import queue
from pathlib import Path

class UDPServer:

    def __init__(self, host, port):
        self.host = host #host do servidor
        self.port = port #porta do servidor
        self.clients = set() #cria conjunto para armazenar endereços dos clientes
        self.nicknames = {} #dicionário do nickname dos clientes
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #criando um socket udp
        self.socket.bind((self.host, self.port))
        print('Aguardando conexão de um cliente')
    
    def broadcast(self):
        while True:
            while not self.messages.empty():
                message, address = self.messages.get() #desempacota a tupla que contém mensagem e endereço que está na fila de mensagem

                if address not in self.clients: #se o endereço não estiver no conjunto de clientes
                    self.clients.add(address) #adiciona no conjunto de endereços
                    print(f'Conexão estabelecida com {address}')
                    self.socket.sendto(f"{address[0]}/{address[1]}".encode('utf-8'), address) #envia para o cliente seu ip e porta (do cliente)

                try:
                    decoded_message = message.decode() #decodifica mensagem
                    if decoded_message.startswith("hi, meu nome eh "): #se cliente estiver se conectando com servidor
                        nickname = decoded_message[16:] #armazena na variável o nickname informado
                        self.nicknames[address] = nickname #adiciona nickname ao dicionário de nicknames com a chave sendo o address
                    else:
                        if decoded_message == "bye":
                            nickname = self.nicknames.get(address, address) #recupera nickname que está no dicionário com base no address
                            print(f'{nickname} saiu do servidor.') #print no terminal do servidor
                            self.send_to_all(f'{nickname} saiu do chat!') #envia mensagem para todos os clientes informando que cliente saiu
                            self.clients.remove(address) #remove cliente da lista de clientes (deveria remover do dicionário tbm, mas não remove)
                        else: #se for uma mensagem normal para enviar
                            client_address = (address[0], address[1]) #tupla que guarda o ip e porta do cliente
                            client_nickname = self.nicknames.get(client_address) #recupera nickname com base no seu address
                            #envia a mensagem para todos
                            self.send_to_all(decoded_message)
                        
                except UnicodeDecodeError:
                    
                    self.send_to_all(message)
                except:
                    pass


    def receive(self):
        while True:
            try:
                message, address = self.socket.recvfrom(1024)
                if message: #se servidor receber mensagem de algum cliente
                    self.messages.put((message, address)) #adiciona tupla contendo mensagem e address na fila messages (que foi declarada na def start)
            except Exception as e: #acho que não faz nada
                pass

    def send_to_all(self, message): #def usado dentro do broadcasting para enviar a mensagem para todos os clientes
        for client in self.clients: #para cada cliente na lista de clientes ele envia a mensagem codificada
            try:
                self.socket.sendto(message.encode('utf-8'), client) #envia mensagem codificada para cada cliente
            except:
                pass

    def start(self):
        self.messages = queue.Queue() #cria fila de mensagens
        thread1 = threading.Thread(target=self.receive) #cria a tread de receive
        thread2 = threading.Thread(target=self.broadcast) #cria a tread de broadcast
        thread1.start()
        thread2.start()

if __name__ == "__main__":
    server = UDPServer("localhost", 50000)
    server.start()
