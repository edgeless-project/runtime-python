import logging
from concurrent import futures
import sys
import argparse
import uuid

import grpc

import services_pb2_grpc
import messages_pb2

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

logger = logging.getLogger(__name__)


class HostServicer(services_pb2_grpc.GuestAPIHost):
    def __init__(self, node_id: str, function_id: str):
        self.instance_id = messages_pb2.InstanceId(
            node_id=node_id, function_id=function_id
        )

    def Cast(self, request, context):
        logger.info("cast() alias = {}, msg = {}".format(request.alias, request.msg))
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def CastRaw(self, request, context):
        logger.info(
            "cast-raw() node_id = {}, function_id = {}, msg = {}".format(
                request.dst.node_id, request.dst.function_id, request.msg
            )
        )
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Call(self, request, context):
        logger.info("call() alias = {}, msg = {}".format(request.alias, request.msg))
        return messages_pb2.CallReturn(type=messages_pb2.CALL_RET, msg=request.msg)

    def CallRaw(self, request, context):
        logger.info(
            "call-raw() node_id = {}, function_id = {}, msg = {}".format(
                request.dst.node_id, request.dst.function_id, request.msg
            )
        )
        return messages_pb2.CallReturn(type=messages_pb2.CALL_RET, msg=request.msg)

    def TelemetryLog(self, request, context):
        logger.info(
            "telemetry-log() level {}, target {}, msg {}".format(
                request.log_level, request.target, request.msg
            )
        )
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Slf(self, request, context):
        return self.instance_id

    def DelayedCast(self, request, context):
        logger.info(
            "cast() alias = {}, msg = {}, delay = {} ms".format(
                request.alias, request.msg, request.delay
            )
        )
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Sync(self, request, context):
        logger.info("sync() msg size {} bytes".format(len(request.serialized_state)))
        return google_dot_protobuf_dot_empty__pb2.Empty()


class NodeEmulator:
    def __init__(
        self,
        port: int,
        function_endpoint: str,
        max_workers: int,
        init_payload: str,
        serialized_state: str,
    ) -> None:
        """Create a node emulator exposing a GuestAPIHost server and using a GuestAPIFunction client"""

        # Create the client
        logger.info(
            "starting a client towards remote host at {}".format(function_endpoint)
        )
        channel = grpc.insecure_channel(function_endpoint)
        self.client = services_pb2_grpc.GuestAPIFunctionStub(channel)

        # Create the server
        logger.info(
            "starting server at [::]:{} with max {} workers".format(port, max_workers)
        )
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        services_pb2_grpc.add_GuestAPIHostServicer_to_server(
            HostServicer(node_id=str(uuid.uuid4()), function_id=str(uuid.uuid4())),
            self.server,
        )
        self.server.add_insecure_port("[::]:{}".format(port))
        self.server.start()

        # Call init()
        self.client.Init(
            messages_pb2.FunctionInstanceInit(
                init_payload=init_payload, serialized_state=serialized_state
            )
        )

    def cast(self, msg: str) -> str:
        self.client.Cast(
            messages_pb2.InputEventData(
                src=messages_pb2.InstanceId(
                    node_id=str(uuid.uuid4()), function_id=str(uuid.uuid4())
                ),
                msg=msg,
            )
        )

    def call(self, msg: str) -> str:
        reply = self.client.Call(
            messages_pb2.InputEventData(
                src=messages_pb2.InstanceId(
                    node_id=str(uuid.uuid4()), function_id=str(uuid.uuid4())
                ),
                msg=msg,
            )
        )
        if reply.type == messages_pb2.CALL_RET:
            return reply.msg
        return ""

    def stop(self) -> None:
        self.client.Stop(google_dot_protobuf_dot_empty__pb2.Empty())

    def wait(self) -> None:
        self.server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        "Run an EDGELESS node CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--log-level", type=str, default="WARNING", help="Set the log level"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=50050,
        help="Listening port",
    )
    parser.add_argument(
        "--function-endpoint",
        type=str,
        default="localhost:50051",
        help="Endpoint (address:port) of the function instance",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=10,
        help="Maximum number of workers",
    )
    parser.add_argument(
        "--init-payload", type=str, default="", help="Payload to be passed to init()"
    )
    parser.add_argument(
        "--serialized-state",
        type=str,
        default="",
        help="Serialized state to be passed to init()",
    )
    args = parser.parse_args()

    node_emulator = NodeEmulator(
        port=args.port,
        function_endpoint=args.function_endpoint,
        max_workers=args.max_workers,
        init_payload=args.init_payload,
        serialized_state=args.serialized_state,
    )

    for line in sys.stdin:
        line = line.rstrip().lower()
        if "quit" == line:
            node_emulator.stop()
            break
        elif len(line) > 5 and "cast " == line[0:5]:
            node_emulator.cast(line[5:])
        elif len(line) > 5 and "call " == line[0:5]:
            print("reply: {}".format(node_emulator.call(line[5:])))
        elif "help" == line:
            print(
                """commands:
                  help         show this help
                  cast MSG     send cast() with given payload 
                  call MSG     send call() with given payload 
                  quit         send a stop() command and quit"""
            )
        else:
            print("unknown command: {}".format(line))
