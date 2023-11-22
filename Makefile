run_cli_pares: pairs.py
	python3 cln_par.py $(arg)

run_serv_pares_1: pairs.py
	python3 svc_par.py $(arg)

run_serv_pares_2: pairs.py
	python3 svc_par.py $(arg) flag

run_serv_central: pairs.py
	python3 svc_cen.py $(arg)

run_cli_central: pairs.py
	python3 cln_cen.py $(arg)

pairs.py: pairs.proto
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pairs.proto

clean:
	rm -f *_pb2.py *_pb2_grpc.py