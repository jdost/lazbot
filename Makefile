PYTHONPATH = PYTHONPATH=$(PWD)/src

run:
	${PYTHONPATH} python ./bin/start

clean:
	rm src/plugins/*.pyc
	rm src/lazbot/*.pyc
