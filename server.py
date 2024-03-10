import socket
import sys
import threading
import queue
from pathlib import Path
import functions


class UDPServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = set()
        self.nicknames = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.received_data = []
        self.ordered_received_data = []
        self.duplicated_data = []
        self.corrupted_data = []
        self.first = 0
        self.pckt
        print('Aguardando conexão de um cliente')

    def broadcast(self):
        while True:
            while not self.messages.empty():
                message, address = self.messages.get()

                if address not in self.clients:
                    self.clients.add(address)
                    print(f'Conexão estabelecida com {address}')
                    self.socket.sendto(
                        f"{address[0]}/{address[1]}".encode('utf-8'), address)

                try:
                    decoded_message = message.decode()

                    if decoded_message.startswith("hi, meu nome eh "):
                        nickname = decoded_message[16:]
                        self.nicknames[address] = nickname
                    else:
                        if decoded_message == "bye":
                            nickname = self.nicknames.get(address, address)
                            print(f'{nickname} saiu do servidor.')
                            self.send_to_all(f'{nickname} saiu do chat!')
                            self.clients.remove(address)
                        else:
                            # Obtenha o endereço completo do cliente
                            client_address = (address[0], address[1])
                            client_nickname = self.nicknames.get(
                                client_address)  # Obtenha o apelido do cliente
                            self.send_to_all(decoded_message)

                except UnicodeDecodeError:
                    # Se a mensagem não puder ser decodificada, ela é tratada como um arquivo
                    self.send_to_all(message)
                except:
                    pass

    def receive(self):
        while True:
            try:
                message, address = self.socket.recvfrom(1024)
                self.pckt += 1
                print("\n------------------------------------------")
                print("\Pacote", self.pckt, "sendo enviado")
                print("------------------------------------------")

                # Extraindo dados do pacote
                origin_port = int(message[0:16], 2)
                destiny_port = int(message[16:32], 2)
                size = int(message[32:48], 2)
                checksum = int(message[48:64], 2)
                seq = int(message[64:65], 2)
                prev_data = data
                data = int(message[65:97], 2)

                sum = functions.checksum(origin_port, destiny_port, size)

                if seq == 1:
                    print("\nPacote ["+str(prev_data) +
                          "] duplicado! Descartando e re-solicitando...")
                    self.corrupted_data.append(prev_data)
                if sum != checksum:
                    print("\nPacote [" + str(data) +
                          "] com erro de bits! Descartando e re-solicitando...")
                    self.corrupted_data.append(data)

                while seq == 1 or sum != checksum:
                    if self.first == 1:
                        try:
                            # Enviando mensagem ao cliente informando pacote duplicado/corrompido
                            self.socket.sendto(message, address)
                        except socket.error as msg:
                            print("\nErro: " + str(msg) + "...")
                            sys.exit()

                if message:
                    self.messages.put((message, address))
            except Exception as e:
                pass

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