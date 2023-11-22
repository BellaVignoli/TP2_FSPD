from concurrent import futures
import grpc
import sys
import pairs_pb2
import pairs_pb2_grpc

def insert(stub, key, description):
    request = pairs_pb2.KeyValue(key=key, value=description)
    response = stub.Insert(request)
    return response.result

def search(stub, key):
    request = pairs_pb2.Key(key=key)
    response = stub.Search(request)
    return response.result

def activation(stub, id):
    request = pairs_pb2.ID(id=id)
    response = stub.Activation(request)
    return response.count

def End(stub):
    request = pairs_pb2.Empty()
    response = stub.End(request)
    return response.result

def main():

    if(len(sys.argv) != 2):
        print("Usage: python3 cln_par.py <port>")
        sys.exit(0)

    port = sys.argv[1]
    channel = grpc.insecure_channel(port)
    stub = pairs_pb2_grpc.PairsServerStub(channel)

    try:
        while True:
            command = input().strip()
            if command.startswith("I,"):
                _, key, description = command.split(",", 2)
                result = insert(stub, int(key), description)
                print(result)
            elif command.startswith("C,"):
                _, key = command.split(",", 1)
                result = search(stub, int(key))
                print(result)
            elif command.startswith("A,"):
                _, id = command.split(",", 1)
                result = activation(stub, id)
                print(result)
            elif command == "T":
                result = End(stub)
                print(result)
                break
    except EOFError:
        channel.close()
        sys.exit(0)

if __name__ == '__main__':
    main()