from concurrent import futures
import grpc
import socket
import threading
import sys
import pairs_pb2
import pairs_pb2_grpc

class PairsServer(pairs_pb2_grpc.PairsServerServicer):
    # Inicialização da classe PairsServer com um dicionário que guarda os pares key-value, um evento de parada e o endereço do servidor
    # A classe PairsServer herda os métodos da classe PairsServerServicer gerada após o proto ser compilado
    def __init__(self, stop_event, address):
        self.pairs = {}
        self.stop_event = stop_event
        self.address = address

    def Insert(self, request, context):
        # Insere um par key-value no dicionárion pairs inicializado anteriormente
        key = request.key
        value = request.value
        # Percore o dicionário para verificar se a chave já existe
        if key in self.pairs:
            # Se a chave já existir, retorna -1
            return pairs_pb2.InsertResponse(result=-1)
        else:
            self.pairs[key] = value
            # Se a chave não existir, retorna 0
            return pairs_pb2.InsertResponse(result=0)

    def Search(self, request, context):
        # Procura um par key-value no dicionário pairs
        key = request.key
        if key in self.pairs:
            # Se a chave existir, retorna o valor dela no dicionário
            return pairs_pb2.SearchResponse(result = self.pairs[key])
        else:
            # Se a chave não existir, retorna uma string vazia
            return pairs_pb2.SearchResponse(result = "")

    def Activation(self, request, context):
        # Caso uma flag seja passada como parâmetro no terminal do cliente de pares, a conexão com o servidor central é feita
        if(len(sys.argv) > 2):
            # Cria um canal de comunicação gRPC com o servidor central
            channel = grpc.insecure_channel(request.id)
            # Cria um stub para o servidor central
            stub = pairs_pb2_grpc.CentralServerStub(channel)
            # Chama o método Register do servidor central passando o id do servidor de pares e as chaves que ele possui -> Envia um request para o servidor central
            response = stub.Register(pairs_pb2.ServerKey(service_id=f"{socket.getfqdn()}:{self.address}", keys=self.pairs.keys()))
            # Retorna a quantidade de chaves que foram registradas no servidor central
            return pairs_pb2.KeyCount(count=response.count)
        # Caso nenhuma flag seja passada como parâmetro no terminal do cliente de pares, a conexão com o servidor central não é feita
        return pairs_pb2.KeyCount(count=0)

    def End(self, request, context):
        #  Seta o evento de parada para que o servidor pare de rodar
        self.stop_event.set()
        # Retorna 0 se o servidor é encerrado com sucesso
        return pairs_pb2.EndResponse(result=0)

def serve():

    if(len(sys.argv) > 3 or len(sys.argv) < 1):
        # Caso o número de argumentos passados seja maior que 3 ou menor que 1, o programa é encerrado
        print("Usage: python3 svc_par.py <port> [flag]")
        sys.exit(0)
    
    if(len(sys.argv) == 2):
        # Caso o número de argumentos passados seja igual a 2, o programa é executado com a porta passada como parâmetro
        port = sys.argv[1]

    if(len(sys.argv) == 3):
        # Caso o número de argumentos passados seja igual a 3, o programa é executado com a porta e a flag passadas como parâmetro
        port = sys.argv[1]
        flag = sys.argv[2]

    # Inicializa o evento de parada
    stop_event = threading.Event()
    # Inicializa o servidor gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Adiciona o servidor de pares ao servidor gRPC
    pairs_pb2_grpc.add_PairsServerServicer_to_server(PairsServer(stop_event, sys.argv[1]), server)
    # Listen to the port
    server.add_insecure_port(f'0.0.0.0:{port}')
    # Inicia o servidor gRPC
    server.start()
    # Espera o evento de parada ser setado
    stop_event.wait()
    # Para o servidor gRPC
    server.stop(0)

if __name__ == '__main__':
    serve()