# runtime-python

Run-time environment in Python for EDGELESS

## How to build

The gRPC API specifications must be imported from the [core EDGELESS project](https://github.com/edgeless-project/edgeless). This can be done automatically with a script, which will also compile the protobuf data structures and stubs:

```bash
BRANCH=125-computational-container-runtime scripts/compile-proto.sh
```

The above step requires protoc and Python gRPC tools, which can be installed with:

```
pip install grpcio-tools
```

## How to create a Docker container

Build with:

```bash
docker build -t edgeless-function .
```

Check with:

```bash
docker image ls edgeless-function
```

## How to run

Assuming that In one shell start the container:

```bash
docker run -it --rm --network host edgeless-function
```

On another launch the node command-line interface emulator:

```bash
python3 src/node_cli.py
```

Examples of commands that you can feed to the emulator:

- `cast recast another-function-alias new-message`: cast a message to the function, which instructs the latter to create an asynchronous event on the target `another-function-alias` with the given message payload
- `stop`: invoke the stop() function handler
- `call noret`: invoke the call() handler in such a way that a no-return reply is generated

When using Docker's host network mode the default values of the command-line arguments of the container and Python scripts should work fine.

If this is not the case, then you can adjust the values to your needs via:

- direct command-line arguments to the node emulator (try with `-h` to see the available options)
- the following environment variables can be passed to Docker using `--env ENV_NAME=env_value`:
  - ENV LOG_LEVEL
  - ENV PORT
  - ENV HOST_ENDPOINT
  - ENV MAX_WORKERS
