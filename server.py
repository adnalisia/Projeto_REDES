import socket
import threading
import queue

class UDPServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = set()
        self.nicknames = {}
        self.fragmented_messages = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        print('Aguardando conexão de um cliente')

    def broadcast(self):
        while True:
            while not self.messages.empty():
                message, address = self.messages.get()

                if address not in self.clients:
                    self.clients.add(address)
                    print(f'Conexão estabelecida com {address}')
                    self.socket.sendto(f"{self.host}/{self.port}".encode('utf-8'), address)

                try:
                    decoded_message = message.decode('utf-8')

                    if 'hi, meu nome eh:' in decoded_message:
                        nickname = decoded_message.split(':', 1)[1].strip()
                        self.nicknames[address] = nickname
                        print(f'O nome de usuário do cliente {address} é {nickname}')
                        self.socket.sendto('Você está conectado!'.encode('utf-8'), address)
                        self.send_to_all(f'{nickname} entrou no chat!'.encode('utf-8'))

                    else:
                        sender_nickname = self.nicknames.get(address)
                        if sender_nickname not in self.fragmented_messages:
                            self.fragmented_messages[sender_nickname] = []

                        if decoded_message == "finish": #final da mensagem fragmentada
                            complete_message = ''.join(self.fragmented_messages[sender_nickname])
                            self.fragmented_messages[sender_nickname] = []
                            self.send_to_all(f"{sender_nickname}: {complete_message}")
                        else:
                            self.fragmented_messages[sender_nickname].append(decoded_message)
                except:
                    client_address = (address[0], address[1])  # Obtenha o endereço completo do cliente
                    client_nickname = self.nicknames.get(client_address)  # Obtenha o apelido do cliente
                    self.clients.remove(client_address)
                    del self.nicknames[client_address]
                    self.socket.sendto(f'{client_nickname} saiu da sala!'.encode('utf-8'), address)

    def receive(self):
        while True:
            try:
                message, address = self.socket.recvfrom(1024)
                if message:
                    self.messages.put((message, address))
            except Exception as e:
                print(f"erro em receive: {e}")

    def send_to_all(self, message):
        for client in self.clients:
            try:
                self.socket.sendto(message.encode('utf-8'), client)
            except:
                pass

    def start(self):
        self.messages = queue.Queue()
        thread1 = threading.Thread(target=self.receive)
        thread2 = threading.Thread(target=self.broadcast)
        thread1.start()
        thread2.start()

if __name__ == "__main__":
    server = UDPServer("localhost", 50000)
    server.start()
