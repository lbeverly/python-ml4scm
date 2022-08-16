dockerbuild:
	docker build -t 'ml4scm-dev:develop' ./environment/ml4scm-dev-docker/

run: dockerbuild
	docker run --rm -it -v $$PWD:/ml4scm -p8888:8888 ml4scm-dev:develop
