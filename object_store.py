import openstack
import openstack.exceptions
import typing
import dotenv
import dataclasses
import os.path
import random
import logging
import constants as c

SW_DOWNLOAD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")

dotenv.load_dotenv()
LOG = logging.getLogger(__name__)
T_OPT_METADATA = typing.Optional[dict[str, str]]


def build_hash_key():
    import string
    chars = list(string.digits + string.ascii_letters + '-_')
    new_key = ""
    while len(chars) > 0:
        new_key += chars.pop(random.randint(0, len(chars) - 1))
    return new_key


HASH_KEY = build_hash_key()
KEY_RANGE = len(HASH_KEY) - 1
_OS_CONNECTION = openstack.connect()

# Create Container if it doesn't exist
__containers = [
    cont.name
    for cont in _OS_CONNECTION.object_store.containers(prefix=c.SWIFT_CONTAINER)
    if cont.name == c.SWIFT_CONTAINER
]
if not __containers:
    _OS_CONNECTION.object_store.create_container(name=c.SWIFT_CONTAINER)


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


def add_object(content: bytes) -> c.T_RESPONSE:
    new_hash = ""
    while not new_hash:
        new_hash = generate_hash()
        test_object = get_object(new_hash)
        if test_object[c.RESP_SUCCESS] and test_object[c.RESP_CONTENT]:
            new_hash = ""
            continue
    try:
        _OS_CONNECTION.object_store.upload_object(
            container=c.SWIFT_CONTAINER, name=new_hash, data=content
        )
    except openstack.exceptions.OpenStackCloudException as e:
        return fail(str(e))
    return good(new_hash)


def drop_object(name: str) -> c.T_RESPONSE:
    _OS_CONNECTION.object_store.delete_object(name, container=c.SWIFT_CONTAINER)
    return good(c.RESP_STATUS_DELETED)


def list_objects(*names: str) -> c.T_RESPONSE:
    contents = []
    names = set(names)
    for obj in _OS_CONNECTION.object_store.objects(container=c.SWIFT_CONTAINER):
        if obj.name in names:
            contents.append(Object(obj.name, obj.content_length, obj.last_modified_at))
    return good(contents)


def get_object(name: str) -> c.T_RESPONSE:
    for obj in _OS_CONNECTION.object_store.objects(
        container=c.SWIFT_CONTAINER, prefix=name
    ):
        return good(Object(obj.name, obj.content_length, obj.last_modified_at))
    return fail("No object found")


def download_content(name: str) -> c.T_RESPONSE:
    content = _OS_CONNECTION.object_store.download_object(name, c.SWIFT_CONTAINER)
    if not os.path.exists(SW_DOWNLOAD_PATH):
        os.mkdir(SW_DOWNLOAD_PATH)
    output_path = os.path.join(SW_DOWNLOAD_PATH, name)
    open(output_path, "wb").write(content)
    return good(output_path)
