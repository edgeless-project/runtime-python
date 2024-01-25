#!/bin/bash

if [ "$BRANCH" == "" ] ; then
  BRANCH=main
fi

if [ ! -d src ] ; then
  echo "Please run this script from the repo root"
  exit 1
fi

python -m grpc_tools.protoc -h >& /dev/null
if [ $? -ne 0 ] ; then
  echo "Please install protoc compiler, see https://grpc.io/docs/languages/python/basics/"
  exit 1
fi

pushd src
wget https://raw.githubusercontent.com/edgeless-project/edgeless/$BRANCH/edgeless_api/proto/services.proto
wget https://raw.githubusercontent.com/edgeless-project/edgeless/$BRANCH/edgeless_api/proto/messages.proto
python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. services.proto
popd
