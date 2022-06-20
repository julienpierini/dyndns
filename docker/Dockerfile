FROM python:3.9.10-slim

COPY src/. src/
RUN pip install -r /src/requirements.txt

ENTRYPOINT python src/main.py