import logging

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

import services_pb2_grpc
import messages_pb2

logger = logging.getLogger(__name__)


class FunctionServicer(services_pb2_grpc.GuestAPIFunction):
    def __init__(self, function_api):
        self.function_api = function_api

    def Init(self, request, context):
        slf = self.function_api.slf()
        logger.info(
            "init() slf node_id {}, function_id {}, payload = {}, serialized state size = {} bytes".format(
                slf.node_id,
                slf.function_id,
                request.init_payload,
                len(request.serialized_state),
            )
        )
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Cast(self, request, context):
        logger.info(
            "cast() src node_id = {}, function_id = {}, msg = {}".format(
                request.src.node_id, request.src.function_id, request.msg
            )
        )
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Call(self, request, context):
        logger.info(
            "cast() src node_id = {}, function_id = {}, msg = {}".format(
                request.src.node_id, request.src.function_id, request.msg
            )
        )
        return messages_pb2.CallReturn(type=messages_pb2.CALL_RET, msg=request.msg)

    def Stop(self, request, context):
        logger.info("stop()")
        return google_dot_protobuf_dot_empty__pb2.Empty()
