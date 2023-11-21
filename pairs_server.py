from concurrent import futures
import grpc
import sys
import pairs_pb2
import pairs_pb2_grpc

class PairsServer(pairs_pb2_grpc.PairsServerServicer):
    def __init__(self):
        self.pairs = {}

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
        return pairs_pb2.Resposta(result=0)

    def End(self, request, context):
        # Lógica de término aqui
        return pairs_pb2.Resposta(EndResponse=0)

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pairs_pb2_grpc.add_PairsServerServicer_to_server(PairsServer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print("Erro")
        sys.exit(1)
    port = sys.argv[1]
    serve(port)