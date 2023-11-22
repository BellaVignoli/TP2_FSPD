import grpc
from concurrent import futures
import threading
import pairs_pb2
import pairs_pb2_grpc
import sys

class CentralServer(pairs_pb2_grpc.CentralServerServicer):
    def __init__(self, stop_event):
        self.keys_dict = {}
        self.stop_event = stop_event

    def Register(self, request, context):
        service_id = request.service_id
        keys = request.keys
        for key in keys:
            self.keys_dict[key] = service_id
        return pairs_pb2.KeyCount(count=len(keys))

    def Map(self, request, context):
        wanted_key = request.key
        for key in self.keys_dict:
            if key == wanted_key:
                return pairs_pb2.ServerID(id = self.keys_dict[key])
        return pairs_pb2.ServerID(id="")

    def End(self, request, context):
        self.stop_event.set()
        # Lógica de término aqui
        return pairs_pb2.EndResponse(result=len(self.keys_dict))

def serve():

    if(len(sys.argv) != 2):
        print("Usage: python3 svc_cen.py <port>")
        sys.exit(0)

    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pairs_pb2_grpc.add_CentralServerServicer_to_server(CentralServer(stop_event), server)
    server.add_insecure_port('[::]:' + sys.argv[1])
    server.start()
    stop_event.wait()
    server.stop(0)

if __name__ == '__main__':
    serve()
