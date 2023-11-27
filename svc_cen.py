import grpc
from concurrent import futures
import threading
import pairs_pb2
import pairs_pb2_grpc
import sys

class CentralServer(pairs_pb2_grpc.CentralServerServicer):
    # Inicialização da classe CentralServer com um dicionário que guarda os pares key-value e um evento de parada
    # A classe CentralServer herda os métodos da classe CentralServerServicer gerada após o proto ser compilado
    def __init__(self, stop_event):
        self.keys_dict = {}
        self.stop_event = stop_event

    def Register(self, request, context):
        # Registra um par service_id-keys no dicionário keys_dict
        service_id = request.service_id
        keys = request.keys
        for key in keys:
            # Percorre o dicionário e registra as chaves que ainda não foram registradas
            self.keys_dict[key] = service_id
        # Retorna a quantidade de chaves que foram registradas no servidor central
        return pairs_pb2.KeyCount(count=len(keys))

    def Map(self, request, context):
        # Mapeia o service_id do servidor de pares que possui a chave passada como parâmetro
        wanted_key = request.key
        # Percorre o dicionário e retorna o service_id do servidor de pares que possui a chave passada como parâmetro
        for key in self.keys_dict:
            if key == wanted_key:
                return pairs_pb2.ServerID(id = self.keys_dict[key])
        # Se a chave não existir, retorna uma string vazia
        return pairs_pb2.ServerID(id="")

    def End(self, request, context):
        #  Seta o evento de parada para que o servidor pare de rodar
        self.stop_event.set()
        # Retorna a quantidade de chaves que foram registradas no servidor central
        return pairs_pb2.EndResponse(result=len(self.keys_dict))

def serve():

    # Verifica se o número de argumentos passados no terminal é igual a 2, caso contrário, o programa é encerrado
    if(len(sys.argv) != 2):
        print("Usage: python3 svc_cen.py <port>")
        sys.exit(0)

    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pairs_pb2_grpc.add_CentralServerServicer_to_server(CentralServer(stop_event), server)
    # Faz o bind do servidor central com o endereço passado como parâmetro no terminal
    server.add_insecure_port(f"0.0.0.0:{sys.argv[1]}")
    server.start()
    stop_event.wait()
    server.stop(0)

if __name__ == '__main__':
    serve()
