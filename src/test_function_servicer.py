# SPDX-FileCopyrightText: © 2024 Claudio Cicconetti <c.cicconetti@iit.cnr.it>
# SPDX-License-Identifier: MIT

import unittest
import grpc
import uuid
from concurrent import futures

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

import services_pb2_grpc
import messages_pb2

import function_servicer


class FunctionApiStub:
    def connect_to_server(
        self, host_endpoint: str, instance_id: messages_pb2.InstanceId
    ) -> None:
        pass

    def cast(self, alias: str, msg: bytes) -> None:
        pass


class TestFunctionServices(unittest.TestCase):
    def test_client_server(self):
        # Create and start a server.
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        services_pb2_grpc.add_GuestAPIFunctionServicer_to_server(
            function_servicer.FunctionServicer(function_api=FunctionApiStub()), server
        )
        server.add_insecure_port("[::]:50051")
        server.start()

        instance_id = messages_pb2.InstanceId(
            node_id=str(uuid.uuid4()), function_id=str(uuid.uuid4())
        )

        # Create and start a client calling all the server methods.
        channel = grpc.insecure_channel("localhost:50051")
        stub = services_pb2_grpc.GuestAPIFunctionStub(channel)
        stub.Boot(
            messages_pb2.BootData(
                guest_api_host_endpoint="http://localhost:50051/",
                instance_id=instance_id,
            )
        )
        stub.Init(
            messages_pb2.FunctionInstanceInit(
                init_payload="init_payload",
                serialized_state=bytes("aaa", encoding="utf8"),
            )
        )
        stub.Cast(
            messages_pb2.InputEventData(
                src=messages_pb2.InstanceId(
                    node_id="my-node-id", function_id="my-fun-id"
                ),
                msg=bytes("event-payload", encoding="utf8"),
            )
        )
        reply = stub.Call(
            messages_pb2.InputEventData(
                src=messages_pb2.InstanceId(
                    node_id="my-node-id", function_id="my-fun-id"
                ),
                msg=bytes("event-payload", encoding="utf8"),
            )
        )
        self.assertEqual(reply.type, messages_pb2.CALL_RET_REPLY)
        self.assertEqual(bytes("event-payload", encoding="utf8"), reply.msg)
        stub.Stop(google_dot_protobuf_dot_empty__pb2.Empty())

        # Terminate
        server.stop(None)


if __name__ == "__main__":
    unittest.main()
