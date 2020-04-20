init:
	pip install -r requirements.txt
test: clean
	python setup.py develop
	pytest --cov=rdp --cov-report html
clean:
	find rdp -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: init test
