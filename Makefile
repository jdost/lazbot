PYTHONPATH = PYTHONPATH=$(PWD)/src

.DEFAULT: test

.PHONY: run shell clean unittest lint test docs-init docs docs-serve docs-publish

run:
	${PYTHONPATH} python ./bin/start

shell:
	@${PYTHONPATH} python ./etc/console.py

clean:
	rm -f src/plugins/*.pyc
	rm -f src/lazbot/*.pyc
	rm -f src/lazbot/*/*.pyc

unittest:
	@echo Core tests:
	@${PYTHONPATH} nosetests ${NOSEOPTS} ./tests/test_*.py
	@echo Plugin tests:
	@${PYTHONPATH} nosetests ${NOSEOPTS} ./tests/plugins/test_*.py

lint:
	@flake8 --ignore=F401,E731 --max-complexity 12 src/
	@flake8 --ignore=F401,E731,E402 --max-complexity 12 tests/

test: lint unittest

docs-init:
	pip install -r docs/requirements.txt

docs: docs-init
	cd docs && make html

docs-serve: docs
	cd docs/build/html/ && python -m SimpleHTTPServer 8080

docs-publish: docs clean
	git co gh-pages
	git ls-files | xargs git rm -f
	mv -f docs/build/html/* .
	touch .nojekyll
	git add .
	git commit -a -m "Docs update"
	git push
	git co master
