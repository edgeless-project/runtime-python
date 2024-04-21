# SPDX-FileCopyrightText: © 2024 Claudio Cicconetti <c.cicconetti@iit.cnr.it>
# SPDX-License-Identifier: MIT

from enum import Enum
import logging
from urllib.parse import urlparse
from time import sleep

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

import services_pb2_grpc
import messages_pb2

logger = logging.getLogger(__name__)


class State(Enum):
    PRE_BOOTED = 1
    BOOTED = 2
    INITIALIZED = 3
    STOPPED = 4
    ERROR = 5


class FunctionServicer(services_pb2_grpc.GuestAPIFunction):
    def __init__(self, function_api):
        self.function_api = function_api
        self.instance_id = None
        self.state = State.PRE_BOOTED

    def Boot(self, request, context):
        logger.info(
            "boot() host_endpoint {} node_id {} function_id {}".format(
                request.guest_api_host_endpoint,
                request.instance_id.node_id,
                request.instance_id.function_id,
            )
        )
        parsed = urlparse(request.guest_api_host_endpoint)
        self.function_api.connect_to_server(
            "{}:{}".format(parsed.hostname, parsed.port), request.instance_id
        )
        self.state = State.BOOTED
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Init(self, request, context):
        logger.info(
            "init() payload = {}, serialized state size = {} bytes".format(
                request.init_payload,
                len(request.serialized_state),
            )
        )
        self.check_state(State.BOOTED)
        self.state = State.INITIALIZED
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Cast(self, request, context):
        logger.info(
            "cast() src node_id = {}, function_id = {}, msg = {}".format(
                request.src.node_id, request.src.function_id, request.msg
            )
        )
        self.check_state(State.INITIALIZED)

        tokens = str(request.msg, encoding="utf8").strip().split(" ")
        if len(tokens) == 3 and "recast" == tokens[0]:
            self.function_api.cast(
                alias=tokens[1], msg=bytes(tokens[2], encoding="utf8")
            )
        elif len(tokens) == 4 and "recast-raw" == tokens[0]:
            self.function_api.cast_raw(
                node_id=tokens[1],
                function_id=tokens[2],
                msg=bytes(tokens[3], encoding="utf8"),
            )
        elif len(tokens) == 4 and "recast-delayed" == tokens[0]:
            self.function_api.delayed_cast(
                delay=int(tokens[1]),
                alias=tokens[2],
                msg=bytes(tokens[3], encoding="utf8"),
            )
        elif len(tokens) == 3 and "telemetry-log" == tokens[0]:
            self.function_api.telemetry_log(
                log_level=messages_pb2.LOG_INFO,
                target=tokens[1],
                msg=bytes(tokens[2], encoding="utf8"),
            )
        elif len(tokens) > 1 and "sync" == tokens[0]:
            self.function_api.sync(
                serialized_state=bytes(" ".join(tokens[1:]), encoding="utf8")
            )
        else:
            sleep(1)
            self.function_api.cast(alias="output", msg=request.msg)

        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Call(self, request, context):
        logger.info(
            "call() src node_id = {}, function_id = {}, msg = {}".format(
                request.src.node_id, request.src.function_id, request.msg
            )
        )
        self.check_state(State.INITIALIZED)

        tokens = str(request.msg, encoding="utf8").strip().split(" ")
        if len(tokens) == 3 and "recall" == tokens[0]:
            self.function_api.call(
                alias=tokens[1], msg=bytes(tokens[2], encoding="utf8")
            )
        elif len(tokens) == 4 and "recall-raw" == tokens[0]:
            self.function_api.call_raw(
                node_id=tokens[1],
                function_id=tokens[2],
                msg=bytes(tokens[3], encoding="utf8"),
            )
        elif len(tokens) == 1 and "noret" == tokens[0]:
            return messages_pb2.CallReturn(type=messages_pb2.CALL_NO_RET)
        elif len(tokens) == 1 and "err" == tokens[0]:
            return messages_pb2.CallReturn(type=messages_pb2.CALL_RET_ERR)

        return messages_pb2.CallReturn(
            type=messages_pb2.CALL_RET_REPLY, msg=request.msg
        )

    def Stop(self, request, context):
        logger.info("stop()")
        self.check_state(State.INITIALIZED)
        self.state = State.STOPPED
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def check_state(self, state: State):
        """Raise exception if the state is not that specified"""

        if self.state != state:
            self.state = State.ERROR
            raise RuntimeError(
                "expected to be in state {}, actual state {}".format(state, self.state)
            )
