import grpc
import pairs_pb2
import pairs_pb2_grpc
import sys

def map(stub, key):
    request = pairs_pb2.Key(key=key)
    response = stub.Map(request)
    return response.id

def termination(stub):
    request = pairs_pb2.Empty()
    response = stub.End(request)
    return response.result

def main():

    port = sys.argv[1]
    channel = grpc.insecure_channel(port)
    stub = pairs_pb2_grpc.CentralServerStub(channel)

    try:
        while True:
            command = input().strip()
            if command.startswith("C,"):
                _, key = command.split(",", 1)
                channel = grpc.insecure_channel(port)
                stub = pairs_pb2_grpc.CentralServerStub(channel)
                service_id = map(stub, int(key))
                if service_id == "":
                    continue
                print(f"{service_id}: ", end="")
                channel = grpc.insecure_channel(service_id)
                stub = pairs_pb2_grpc.PairsServerStub(channel)
                request = pairs_pb2.Key(key=int(key))
                response = stub.Search(request)
                print(response.result)

            elif command == "T":
                result = termination(stub)
                print(result)
                break
    except EOFError:
        channel.close()
        sys.exit(0)

if __name__ == '__main__':
    main()