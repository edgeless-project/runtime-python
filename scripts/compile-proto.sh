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

proto_files="services messages"

pushd src
for proto_file in $proto_files ; do
  wget https://raw.githubusercontent.com/edgeless-project/edgeless/$BRANCH/edgeless_api/proto/$proto_file.proto
done
for proto_file in $proto_files ; do
  python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. $proto_file.proto
done
popd
