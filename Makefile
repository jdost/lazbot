PYTHONPATH = PYTHONPATH=$(PWD)/src

run:
	${PYTHONPATH} python ./bin/start

shell:
	${PYTHONPATH} python ./etc/console.py

clean:
	rm src/plugins/*.pyc
	rm src/lazbot/*.pyc
