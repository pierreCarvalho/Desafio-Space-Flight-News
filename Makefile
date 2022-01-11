run:
	uvicorn app.main:app --reload
req:
	pipenv run pip freeze > requirements.txt