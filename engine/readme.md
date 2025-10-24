# TODO: write project setup guide and an engine guide on how to etc etc


protoc generation command 

python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. ./src/proto/lob.proto