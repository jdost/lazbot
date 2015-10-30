PYTHONPATH = PYTHONPATH=$(PWD)/src

run:
	${PYTHONPATH} python ./bin/start

shell:
	${PYTHONPATH} python ./etc/console.py

clean:
	rm src/plugins/*.pyc
	rm src/lazbot/*.pyc

unittest:
	${PYTHONPATH} nosetests ${NOSEOPTS} ./tests/test_*.py

lint:
	flake8 --ignore=F401 --max-complexity 12 src/
	flake8 --ignore=F401 --max-complexity 12 tests/

test: lint unittest

docs-init:
	pip install -r docs/requirements.txt

docs: docs-init
	cd docs && make html

docs-serve:
	cd docs/build/html/ && python -m SimpleHTTPServer 8080

docs-publish: clean docs
	git co gh-pages
	mv docs/build/html/* .
	git commit -a
	git push
