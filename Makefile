install:
	poetry install

export_requirments.txt:
	poetry export -f requirements.txt --output requirements.txt

docker_image:
	docker build -t stackoverflow-etl .

start_docker_container:
	docker run -d --name stackoverflow-etl -p 5000:5000 stackoverflow-etl

format:
	bash scripts/format.sh

test:
	pytest --cov=app 