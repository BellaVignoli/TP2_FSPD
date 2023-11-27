from concurrent import futures
import grpc
import socket
import threading
import sys
import pairs_pb2
import pairs_pb2_grpc

class PairsServer(pairs_pb2_grpc.PairsServerServicer):
    def __init__(self, stop_event, address):
        self.pairs = {}
        self.stop_event = stop_event
        self.address = address

    def Insert(self, request, context):
        key = request.key
        value = request.value
        if key in self.pairs:
            return pairs_pb2.InsertResponse(result=-1)
        else:
            self.pairs[key] = value
            return pairs_pb2.InsertResponse(result=0)

    def Search(self, request, context):
        key = request.key
        if key in self.pairs:
            return pairs_pb2.SearchResponse(result = self.pairs[key])
        else:
            return pairs_pb2.SearchResponse(result = "")

    def Activation(self, request, context):
        # Lógica de ativação aqui
        if(len(sys.argv) > 2):
            channel = grpc.insecure_channel(request.id)
            stub = pairs_pb2_grpc.CentralServerStub(channel)
            response = stub.Register(pairs_pb2.ServerKey(service_id=f"{socket.getfqdn()}:{self.address}", keys=self.pairs.keys()))
            return pairs_pb2.KeyCount(count=response.count)
        return pairs_pb2.KeyCount(count=0)

    def End(self, request, context):
        # Lógica de término aqui
        self.stop_event.set()
        return pairs_pb2.EndResponse(result=0)

def serve():

    if(len(sys.argv) > 3 or len(sys.argv) < 1):
        print("Usage: python3 svc_par.py <port> [flag]")
        sys.exit(0)
    
    if(len(sys.argv) == 2):
        port = sys.argv[1]

    if(len(sys.argv) == 3):
        port = sys.argv[1]
        flag = sys.argv[2]

    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pairs_pb2_grpc.add_PairsServerServicer_to_server(PairsServer(stop_event, sys.argv[1]), server)
    server.add_insecure_port(f'0.0.0.0:{port}')
    server.start()
    stop_event.wait()
    server.stop(0)

if __name__ == '__main__':
    serve()