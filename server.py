import socket
import threading
import queue
from pathlib import Path

class UDPServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = set()
        self.nicknames = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        print('Aguardando conexão de um cliente')
    
    def broadcast(self):
        while True:
            while not self.messages.empty():
                #desempacota a tupla que contém mensagem e endereço que está na fila de mensagem
                message, address = self.messages.get()

                if address not in self.clients: #se o endereço não estiver na lista de clientes
                    self.clients.add(address) #adiciona na lista de endereços
                    print(f'Conexão estabelecida com {address}')
                    #envia para o cliente seu ip e porta (do cliente)
                    self.socket.sendto(f"{address[0]}/{address[1]}".encode('utf-8'), address)

                try:
                    decoded_message = message.decode() #decodifica mensagem
                    #se cliente estiver se conectando com servidor
                    if decoded_message.startswith("hi, meu nome eh "):
                        nickname = decoded_message[16:]
                        #adiciona nickname ao dicionário de nicknames com a chave sendo o address
                        self.nicknames[address] = nickname
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
                #se servidor receber mensagem de algum cliente
                if message:
                    #adiciona tupla contendo mensagem e address na fila mensagens (que está na def start)
                    self.messages.put((message, address))
            except Exception as e: #acho que não faz nada
                pass

    #def usado dentro do broadcasting para enviar a mensagem para todos os clientes
    def send_to_all(self, message):
        #para cada cliente na lista de clientes ele envia a mensagem codificada
        for client in self.clients:
            try:
                self.socket.sendto(message.encode('utf-8'), client)
            except:
                pass

    def start(self):
        self.messages = queue.Queue() #cria fila de mensagens
        thread1 = threading.Thread(target=self.receive)
        thread2 = threading.Thread(target=self.broadcast)
        thread1.start()
        thread2.start()

if __name__ == "__main__":
    server = UDPServer("localhost", 50000)
    server.start()
