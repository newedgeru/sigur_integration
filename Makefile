horoshkola:
	ssh -L 18080:localhost:18080 iva@10.18.60.70

netshoot:
	docker run --rm -it --network=ivacv19090 nicolaka/netshoot

tests:
	python src/tests/send_logs.py

exec:
	docker-compose exec sigur_integration bash