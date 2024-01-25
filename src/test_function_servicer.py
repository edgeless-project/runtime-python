import unittest
import grpc
from concurrent import futures

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

import services_pb2_grpc
import messages_pb2

import function_servicer


class FunctionApiStub:
    def slf(self) -> messages_pb2.InstanceId:
        return messages_pb2.InstanceId(
            node_id="slf-node-id", function_id="slf-function-id"
        )


class TestFunctionServices(unittest.TestCase):
    def test_client_server(self):
        # Create and start a server.
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        services_pb2_grpc.add_GuestAPIFunctionServicer_to_server(
            function_servicer.FunctionServicer(function_api=FunctionApiStub()), server
        )
        server.add_insecure_port("[::]:50051")
        server.start()

        # Create and start a client calling all the server methods.
        channel = grpc.insecure_channel("localhost:50051")
        stub = services_pb2_grpc.GuestAPIFunctionStub(channel)
        stub.Init(
            messages_pb2.FunctionInstanceInit(
                init_payload="init_payload", serialized_state="aaa"
            )
        )
        stub.Cast(
            messages_pb2.InputEventData(
                src=messages_pb2.InstanceId(
                    node_id="my-node-id", function_id="my-fun-id"
                ),
                msg="event-payload",
            )
        )
        reply = stub.Call(
            messages_pb2.InputEventData(
                src=messages_pb2.InstanceId(
                    node_id="my-node-id", function_id="my-fun-id"
                ),
                msg="event-payload",
            )
        )
        self.assertEqual(reply.type, messages_pb2.CALL_RET_REPLY)
        self.assertEqual("event-payload", reply.msg)
        stub.Stop(google_dot_protobuf_dot_empty__pb2.Empty())

        # Terminate
        server.stop(None)


if __name__ == "__main__":
    unittest.main()
