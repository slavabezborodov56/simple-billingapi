FROM python:3.9

COPY . .

RUN pip install poetry && poetry install

ENV APPLICATION_NAME simple-billingapi

EXPOSE 8000

CMD ["poetry", "run", "simple-billingapi", "serve", "--host", "0.0.0.0", "--port", "8000"]
