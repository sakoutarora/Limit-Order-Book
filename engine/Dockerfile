FROM python:3.10-slim
WORKDIR /app
COPY ./src/demo.py .
RUN pip install pysyncobj flask
CMD ["python", "demo.py"]