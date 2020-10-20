up:
	docker-compose \
		-f ./docker-compose.yml \
		up

down:
	docker-compose \
		-f ./docker-compose.yml \
		down \
		--remove-orphans
