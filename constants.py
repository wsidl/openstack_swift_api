import typing

SWIFT_CONTAINER = "web_api"

DT_FORMAT = "%Y-%m-%d %H:%M:%S"

RESP_SUCCESS = "is_success"
RESP_CONTENT = "content"
RESP_MESSAGE = "message"

RESP_STATUS_DELETED = "Deleted"

SW_ERR_GET_META = "Swift Object retrieval generated an error: %s"
SW_ERR_DL_CONTENT = "Unknown Error retrieving object contents: %s"


class ResponseSuccess(typing.TypedDict):
    is_success: bool
    content: typing.Any


class ResponseFail(typing.TypedDict):
    is_success: bool
    message: str


T_RESPONSE = typing.Union[ResponseFail, ResponseSuccess]
