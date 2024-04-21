![](edgeless-logo-64-40.png)
![](https://www.python.org/static/community_logos/python-powered-w-100x40.png)

# runtime-python

Run-time environment in Python for
[EDGELESS](https://edgeless-project.eu/).

## How to build

The gRPC API specifications must be imported from the
[core EDGELESS project](https://github.com/edgeless-project/edgeless).
This can be done automatically with a script, which will also compile the
protobuf data structures and stubs:

```bash
scripts/compile-proto.sh
```

The above step requires protoc and Python gRPC tools, which can be installed
with:

```
pip install grpcio-tools
```

## How to create a Docker container

Make sure you have Docker installed, if not
[get Docker](https://docs.docker.com/get-docker/).

Build the container with:

```bash
docker build -t python-function .
```

Check it with:

```bash
docker image ls python-function
```

## How to run

In one shell start the container:

```bash
docker run -it --rm --network host python-function
```

In another launch the EDGELESS node command-line interface emulator:

```bash
python3 src/node_cli.py
```

Examples of commands that you can feed to the emulator:

- `cast recast another-function-alias new-message`: cast a message to the
  function, which instructs the latter to create an asynchronous event on the
  target `another-function-alias` with the given message payload
- `stop`: invoke the stop() function handler
- `call noret`: invoke the call() handler in such a way that a no-return reply
  is generated
- `cast sync inner-function-state`: triggers the function to invoke a state
  synchronization primitive

When using Docker's host network mode the default values of the command-line
arguments of the container and Python scripts should work fine.

If this is not the case, then you can adjust the values to your needs via:

- direct command-line arguments to the node emulator (try with `-h` to see the
  available options)
- the following environment variables can be passed to Docker using
  `--env ENV_NAME=env_value`:
  - ENV LOG_LEVEL
  - ENV PORT
  - ENV MAX_WORKERS

### Run without Docker

For development/troubleshooting you can also start directly the function:

```bash
python3 src/function.py
```

### Run on Docker without host network

The `--network host` option makes the function application listens to a port
on the host. If this is not possible, then you will have to publish the port:

```bash
docker run -it --rm -P python-function
```

At this point you have to learn what is the public port to which Docker mapped
the private port inside the container.

First, get the name of the container with:

```bash
docker ps -a -f ancestor=python-function
```

With some luck, you should be able to retrieve the port mapping of the
container with this command:

```bash
docker port $(docker ps -a -f ancestor=python-function -q | head -n 1)
```

which will produce an output like the following:

```
7101/tcp -> 0.0.0.0:32815
7101/tcp -> [::]:32809
```

In this example, the private port 7101 for IPv4 was mapped to port 32815.

Then you can run the node emulator with:

```bash
python3 src/node_cli.py --function-endpoint 127.0.0.1:32815 --host-endpoint 10.1.1.2:50050
```

where `--function-endpoint` specifies the public port mapped by Docker for the
function running in the container (32815 in our example) and
`--host-endpoint` must be an end-point with an address that is reachable from
the container (run `hostname -I` for your options) and a free TCP port
(50050 in the example).

## License

The Repository is licensed under the MIT License. Please refer to
[LICENSE](LICENSE) and [CONTRIBUTORS.txt](CONTRIBUTORS.txt). 

## Funding

EDGELESS received funding from the [European Health and Digital Executive Agency
 (HADEA)](https://hadea.ec.europa.eu/) program under Grant Agreement No 101092950.
