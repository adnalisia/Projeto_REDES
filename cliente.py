import socket
import threading


def receber_mensagens(client_socket):
    while True:
        try:
            data, _ = client_socket.recvfrom(1024)  # Recebe dados do servidor
            print(f"Servidor: {data.decode('utf-8')}")
        except ConnectionResetError:
            break

def enviar_mensagens(server_address):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP

    receive_thread = threading.Thread(target=receber_mensagens, args=(client_socket,))
    receive_thread.start()

    while True:
        message = input("Digite a mensagem: ")
        client_socket.sendto(message.encode('utf-8'), server_address)  # Envia mensagem para o servidor


server_ip = '127.0.0.1'  # Endereço IP do servidor
server_port = 9999  # Porta do servidor

server_address = (server_ip, server_port)  # Endereço do servidor

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP
client_socket.bind(('127.0.0.1', 0))  # Vincula a um endereço local e porta aleatória

client_socket.sendto(b"Conectar ao servidor", server_address)  # Envia uma mensagem para conectar ao servidor