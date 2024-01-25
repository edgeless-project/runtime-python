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

        tokens = request.msg.strip().split(' ')
        if len(tokens) == 3 and 'recast' == tokens[0]:
            self.function_api.cast(alias=tokens[1], msg=tokens[2])
        elif len(tokens) == 4 and 'recast-raw' == tokens[0]:
            self.function_api.cast_raw(node_id=tokens[1], function_id=tokens[2], msg=tokens[3])
        elif len(tokens) == 4 and 'recast-delayed' == tokens[0]:
            self.function_api.delayed_cast(delay=int(tokens[1]), alias=tokens[2], msg=tokens[3])
        elif len(tokens) == 3 and 'telemetry-log' == tokens[0]:
            self.function_api.telemetry_log(log_level=messages_pb2.LOG_INFO, target=tokens[1], msg=tokens[2])
    

        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Call(self, request, context):
        logger.info(
            "cast() src node_id = {}, function_id = {}, msg = {}".format(
                request.src.node_id, request.src.function_id, request.msg
            )
        )

        tokens = request.msg.strip().split(' ')
        if len(tokens) == 3 and 'recall' == tokens[0]:
            self.function_api.call(alias=tokens[1], msg=tokens[2])
        elif len(tokens) == 4 and 'recall-raw' == tokens[0]:
            self.function_api.call_raw(node_id=tokens[1], function_id=tokens[2], msg=tokens[3])
        elif len(tokens) == 1 and 'noret' == tokens[0]:
            return messages_pb2.CallReturn(type=messages_pb2.CALL_NO_RET)
        elif len(tokens) == 1 and 'err' == tokens[0]:
            return messages_pb2.CallReturn(type=messages_pb2.CALL_RET_ERR)
        
        return messages_pb2.CallReturn(type=messages_pb2.CALL_RET_REPLY, msg=request.msg)

    def Stop(self, request, context):
        logger.info("stop()")
        return google_dot_protobuf_dot_empty__pb2.Empty()
