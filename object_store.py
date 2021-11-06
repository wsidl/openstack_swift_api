from swiftclient import service, multithreading
import typing
import functools
import os
import dotenv
import dataclasses
from datetime import datetime
import random
import logging
import constants as c

SW_PAGE = "page"
SW_SUCCESS = "success"
SW_OBJECT = "object"
SW_ERROR = "error"
SW_DL_PATH = "path"
SW_UL_ACTION = "action"
SW_UL_ACTION_UPLOAD = "upload_object"
SW_GET_RESP_DICT = "response_dict"
SW_GET_RESP_DICTS = "response_dicts"
SW_GET_HEADERS = "headers"
SW_GET_HD_CONTENT = "content-length"
SW_GET_HD_MTIME = "x-object-meta-mtime"

dotenv.load_dotenv()
LOG = logging.getLogger(__name__)
CONTAINER = c.SWIFT_CONTAINER
__AUTH = {
    "auth_version": os.environ.get("OS_IDENTITY_API_VERSION", "3"),
    "os_username": os.environ.get("OS_USERNAME"),
    "os_password": os.environ.get("OS_PASSWORD"),
    "os_project_id": os.environ.get("OS_PROJECT_ID"),
    "os_project_domain_id": os.environ.get("OS_PROJECT_DOMAIN_ID"),
    "os_auth_url": os.environ.get("OS_AUTH_URL"),
}
T_OPT_METADATA = typing.Optional[dict[str, str]]
HASH_KEY = "lz2_6Uveb1BqWx0CPYuo-GT8fKIAyErRm4piQhNgZVdHD9wJMFnsXatkS7jc53OL"
KEY_RANGE = len(HASH_KEY) - 1


def fail(message: str) -> c.ResponseFail:
    return {c.RESP_SUCCESS: False, c.RESP_MESSAGE: message}


def good(content: typing.Any) -> c.ResponseSuccess:
    return {c.RESP_SUCCESS: True, c.RESP_CONTENT: content}


@dataclasses.dataclass
class Object:
    name: str
    size: int
    updated: str


def generate_hash() -> str:
    length = random.randint(12, 32)
    key = ""
    for _ in range(0, length):
        key += HASH_KEY[random.randint(0, KEY_RANGE)]
    return key


def get_client(func):
    @functools.wraps(func)
    def __get_client(*args, **kwargs):
        with service.SwiftService(__AUTH) as swift:
            try:
                return func(swift, *args, **kwargs)
            except service.SwiftError as e:
                LOG.exception("Unhandled Exception in Swift Connection: %s", str(e))
                raise ConnectionError(str(e))

    return __get_client


@get_client
def add_object(swift: service.SwiftService, content: bytes) -> c.T_RESPONSE:
    with multithreading.OutputManager():
        new_hash = ""
        while not new_hash:
            new_hash = generate_hash()
            test_object = get_object(new_hash)
            if test_object[c.RESP_SUCCESS] and test_object[c.RESP_CONTENT]:
                new_hash = ""
                continue
        new_object = service.SwiftUploadObject(content, new_hash)
        for response in swift.upload(CONTAINER, [new_object]):
            if response[SW_UL_ACTION] != SW_UL_ACTION_UPLOAD:
                continue
            if response[SW_SUCCESS]:
                return good(new_hash)


@get_client
def drop_object(swift: service.SwiftService, name: str) -> c.T_RESPONSE:
    for page in swift.delete(container=CONTAINER, objects=[name]):
        if not page[SW_SUCCESS]:
            return fail(page[SW_ERROR])
        return good(c.RESP_STATUS_DELETED)


@get_client
def get_object(swift: service.SwiftService, object_names: list[str]) -> c.T_RESPONSE:
    contents = []
    for page in swift.download(container=CONTAINER, objects=list(object_names)):
        if not page[SW_SUCCESS]:
            LOG.error(c.SW_ERR_GET_META, str(page[SW_ERROR]))
            return fail(page[SW_ERROR])
        headers = page[SW_GET_RESP_DICT][SW_GET_RESP_DICTS][0][SW_GET_HEADERS]
        contents.append(Object(
            page[SW_OBJECT],
            int(headers[SW_GET_HD_CONTENT]),
            (
                datetime
                .fromtimestamp(float(headers[SW_GET_HD_MTIME]))
                .strftime(c.DT_FORMAT)
            )
        ))
    return good(contents)


@get_client
def download_content(swift: service.SwiftService, name: str) -> c.T_RESPONSE:
    for page in swift.download(container=CONTAINER, objects=[name]):
        if not page[SW_SUCCESS]:
            LOG.error(c.SW_ERR_DL_CONTENT, str(page[SW_ERROR]))
            print(page)
            return fail(page[SW_PAGE])
        return good(page[SW_DL_PATH])
