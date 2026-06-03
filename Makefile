init:
	pip install -r requirements.txt -r requirements-test.txt

test:
	python demo_app/manage.py test data_replication --settings=demo_app.settings_test
