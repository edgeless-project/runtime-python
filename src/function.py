import logging
from concurrent import futures
import sys
import argparse

import grpc

import services_pb2_grpc
import messages_pb2
import function_servicer

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

logger = logging.getLogger(__name__)


class Function:
    def __init__(self, port: int, host_endpoint: str, max_workers: int) -> None:
        """Create a function instance exposing a GuestAPIFunction server and using a GuestAPIHost client"""

        # Create the client
        logger.info("starting a client towards remote host at {}".format(host_endpoint))
        channel = grpc.insecure_channel(host_endpoint)
        self.client = services_pb2_grpc.GuestAPIHostStub(channel)

        # Create the server
        logger.info(
            "starting server at [::]:{} with max {} workers".format(port, max_workers)
        )
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        services_pb2_grpc.add_GuestAPIFunctionServicer_to_server(
            function_servicer.FunctionServicer(self), self.server
        )
        self.server.add_insecure_port("[::]:{}".format(port))
        self.server.start()

    def cast(self, alias: str, msg: str) -> None:
        self.client.Cast(messages_pb2.OutputEventData(alias=alias, msg=msg))

    def cast_raw(self, node_id: str, function_id: str, msg: str) -> None:
        self.client.Cast(
            messages_pb2.OutputEventDataRaw(
                instance_id=messages_pb2.InstanceId(
                    node_id=node_id, function_id=function_id
                ),
                msg=msg,
            )
        )

    def call(self, alias: str, msg: str) -> messages_pb2.CallReturn:
        return self.client.Call(messages_pb2.OutputEventData(alias=alias, msg=msg))

    def call_raw(
        self, node_id: str, function_id: str, msg: str
    ) -> messages_pb2.CallReturn:
        return self.client.CallRaw(
            messages_pb2.OutputEventDataRaw(
                instance_id=messages_pb2.InstanceId(
                    node_id=node_id, function_id=function_id
                ),
                msg=msg,
            )
        )

    def telemetry_log(self, log_level: int, target: str, msg: str) -> None:
        self.client.TelemetryLog(
            messages_pb2.TelemetryLogEvent(log_level=log_level, target=target, msg=msg)
        )

    def slf(self) -> messages_pb2.InstanceId:
        return self.client.Slf(google_dot_protobuf_dot_empty__pb2.Empty())

    def delayed_cast(self, delay: int, alias: str, msg: str) -> None:
        self.client.DelayedCastCast(
            messages_pb2.DelayedEventDataEventData(alias=alias, msg=msg, delay=delay)
        )

    def wait(self) -> None:
        self.server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    logging.getLogger("function_servicer").setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        "Run an EDGELESS function instance",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--log-level", type=str, default="WARNING", help="Set the log level"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=50051,
        help="Listening port",
    )
    parser.add_argument(
        "--host-endpoint",
        type=str,
        default="localhost:50050",
        help="Endpoint (address:port) of the host",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=10,
        help="Maximum number of workers",
    )
    args = parser.parse_args()

    function = Function(
        port=args.port, host_endpoint=args.host_endpoint, max_workers=args.max_workers
    )
    function.wait()
