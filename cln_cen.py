import grpc
import pairs_pb2
import pairs_pb2_grpc
import sys

def map(stub, key):
    # Mapeia e retorna o id que possui a chave passada como parâmetro -> Envia um request para o servidor central
    request = pairs_pb2.Key(key=key)
    response = stub.Map(request)
    return response.id

def termination(stub):
    # Chama o método End do servidor central -> Envia um request para o servidor central
    # Termina o servidor central
    request = pairs_pb2.Empty()
    response = stub.End(request)
    # Retorna a quantidade de chaves que foram registradas no servidor central
    return response.result

def main():

    # Verifica se o número de argumentos passados no terminal é igual a 2, caso contrário, o programa é encerrado
    if(len(sys.argv) != 2):
        print("Usage: python3 cln_cen.py <port>")
        sys.exit(0)

    port = sys.argv[1]
    channel = grpc.insecure_channel(port)
    stub = pairs_pb2_grpc.CentralServerStub(channel)

    try:
        while True:
            command = input().strip()
            # Verifica se o comando passado no terminal começa com C, caso sim, o comando é tratado como uma busca
            if command.startswith("C,"):
                _, key = command.split(",", 1)
                # Mapeia o service_id que possui a chave passada como parâmetro
                service_id = map(stub, int(key))
                # Verifica se o service_id é uma string vazia, caso sim, a chave não existe no servidor central
                if service_id == "":
                    continue
                # Imprime o conteúdo da chave que foi mapeada
                print(f"{service_id}: ", end="")
                # Cria um canal de comunicação gRPC com o servidor de pares
                channel_content = grpc.insecure_channel(service_id)
                # Cria um stub para o servidor de pares
                stub_content = pairs_pb2_grpc.PairsServerStub(channel_content)
                # Chama o método Search do servidor de pares passando a chave que foi mapeada -> Envia um request para o servidor de pares
                request = pairs_pb2.Key(key=int(key))
                # Imprime o resultado da busca que segue as condições do método Search da classe PairsServer, isto é, a resposta enviada pelo servidor
                response = stub_content.Search(request)
                print(response.result)

            # Verifica se o comando passado no terminal começa com T, caso sim, o comando é tratado como uma terminação
            elif command == "T":
                result = termination(stub)
                print(result)
                break
    # Quando chegar no final do arquivo, o programa é encerrado e o canal de comunicação gRPC é fechado
    except EOFError:
        channel.close()
        sys.exit(0)

if __name__ == '__main__':
    main()