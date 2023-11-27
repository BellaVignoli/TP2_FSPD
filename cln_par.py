from concurrent import futures
import grpc
import sys
import pairs_pb2
import pairs_pb2_grpc

def insert(stub, key, description):
    # Insere um par key-value no dicionário pairs
    request = pairs_pb2.KeyValue(key=key, value=description)
    response = stub.Insert(request)
    # Imprime o resultado da inserção que segue as condiçẽos do método Insert da classe PairsServer, isto é, a resposta enviada pelo servidor
    return response.result

def search(stub, key):
    # Procura um par key-value no dicionário pairs
    request = pairs_pb2.Key(key=key)
    response = stub.Search(request)
    # Imprime o resultado da busca que segue as condiçẽos do método Search da classe PairsServer, isto é, a resposta enviada pelo servidor
    return response.result

def activation(stub, id):
    # Chama o método Activation do servidor de pares passando o id do servidor central -> Envia um request para o servidor de pares
    request = pairs_pb2.ID(id=id)
    response = stub.Activation(request)
    # Retorna a quantidade de chaves que foram registradas no servidor central
    return response.count

def End(stub):
    # Chama o método End do servidor de pares -> Envia um request para o servidor de pares
    request = pairs_pb2.Empty()
    response = stub.End(request)
    # Retorna 0 se o servidor é encerrado com sucesso
    return response.result

def main():

    # Verifica se o número de argumentos passados no terminal é igual a 2, caso contrário, o programa é encerrado
    if(len(sys.argv) != 2):
        print("Usage: python3 cln_par.py <port>")
        sys.exit(0)

    port = sys.argv[1]
    # Cria um canal de comunicação gRPC com o servidor de pares
    channel = grpc.insecure_channel(port)
    # Cria um stub para o servidor de pares
    stub = pairs_pb2_grpc.PairsServerStub(channel)

    try:
        while True:
            command = input().strip()
            # Verifica se o comando passado no terminal começa com I, caso sim, o comando é tratado como uma inserção
            if command.startswith("I,"):
                _, key, description = command.split(",", 2)
                result = insert(stub, int(key), description)
                print(result)
            # Verifica se o comando passado no terminal começa com C, caso sim, o comando é tratado como uma busca
            elif command.startswith("C,"):
                _, key = command.split(",", 1)
                result = search(stub, int(key))
                print(result)
            # Verifica se o comando passado no terminal começa com A, caso sim, o comando é tratado como uma ativação
            elif command.startswith("A,"):
                _, id = command.split(",", 1)
                result = activation(stub, id)
                print(result)
            # Verifica se o comando passado no terminal é T, caso sim, o comando é tratado como um término
            elif command == "T":
                result = End(stub)
                print(result)
                break
    # Caso o cliente chegue ao fim do arquivo, o canal de comunicação é fechado e o programa é encerrado
    except EOFError:
        channel.close()
        sys.exit(0)

if __name__ == '__main__':
    main()