FROM python:3.10-slim
WORKDIR /app
RUN pip install grpcio grpcio-tools sortedcontainers
COPY . .
EXPOSE 50051
CMD ["python", "-m", "src"]