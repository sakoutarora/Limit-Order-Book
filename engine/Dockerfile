FROM python:3.10-slim
WORKDIR /app
COPY ./src/demo.py .
RUN pip install grpcio grpcio-tools
CMD ["python", "demo.py"]