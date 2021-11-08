import typing
from flask import Flask, send_file, jsonify, Response, request
from werkzeug import utils
from os import path, mkdir
import json
from lib import object_store, metadata, constants as c

app = Flask(__name__, static_folder="ui/dist", static_url_path="")
UPLOAD_DIR = "/tmp/_srv"
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

if not path.exists(UPLOAD_DIR):
    mkdir(UPLOAD_DIR)


T_TAG = (str, str)
T_TAGS = list[T_TAG]


class Object(typing.TypedDict):
    id: int
    name: str
    size: int
    updated: str
    metadata: T_TAGS


def bad_response(message: str) -> Response:
    return jsonify({"status": "error", "message": message})


def good_response(content: typing.Any) -> Response:
    return jsonify({"status": "success", "content": content})


@app.get("/")
def index():
    return send_file("ui/dist/index.html", mimetype="text/html")


@app.get("/obj")
def get_object_list(search: str = "") -> Response:
    objects: list[Object] = []
    m_ids = metadata.find_object(search)
    m_objs = {
        obj.hash_string: obj for obj in [metadata.get_object(m_oid) for m_oid in m_ids]
    }
    os_response = object_store.list_objects(*list(m_objs))
    if not os_response[c.RESP_SUCCESS]:
        raise bad_response(os_response[c.RESP_CONTENT])
    for obj in os_response[c.RESP_CONTENT]:
        m_obj = m_objs[obj.name]
        objects.append(
            {
                "id": m_obj.id,
                "name": m_obj.name,
                "size": obj.size,
                "updated": obj.updated,
                "metadata": m_obj.all_metadata(),
            }
        )
    return good_response(objects)


@app.put("/obj")
def add_object():
    new_file = request.files["file"]
    if not new_file:
        return bad_response("No file was submitted")
    file_path = path.join(
        app.config["UPLOAD_FOLDER"], utils.secure_filename(new_file.filename)
    )
    new_file.save(file_path)
    file_contents = open(file_path, "rb")
    new_name = request.form["name"]
    tags = json.loads(request.form["tags"])
    response = object_store.add_object(file_contents)
    if not response[c.RESP_SUCCESS]:
        return bad_response(response[c.RESP_MESSAGE])
    new_id = metadata.add_object(new_name, response[c.RESP_CONTENT], *tags)
    return good_response({"new_id": new_id})


@app.delete("/obj/<int:object_id>")
def delete_object(object_id: int):
    current = metadata.get_object(object_id)
    response = object_store.drop_object(current.hash_string)
    if not response[c.RESP_SUCCESS]:
        return bad_response(response[c.RESP_MESSAGE])
    metadata.remove_object(object_id)
    return good_response("deleted")


@app.get("/obj/<int:object_id>/download")
def download_object(object_id: int):
    current = metadata.get_object(object_id)
    response = object_store.download_content(current.hash_string)
    if not response[c.RESP_SUCCESS]:
        return bad_response(response[c.RESP_MESSAGE])
    extension = current.metadata("format") or [".txt"]
    file_name = f"{current.name}.{extension[0]}"
    return send_file(
        response[c.RESP_CONTENT],
        as_attachment=True,
        download_name=file_name,
        attachment_filename=file_name,
    )


@app.post("/obj/<int:object_id>/name/<name>")
def update_object_name(object_id: int, name: str):
    metadata.update_object_name(object_id, name)
    return good_response("Changed")


@app.put("/obj/<int:object_id>/tag/<tag>/<value>")
def set_tag(object_id: int, tag: str, value: str):
    metadata.set_metadata(object_id, (tag, value))
    return good_response("Saved")


@app.delete("/obj/<int:object_id>/tag/<tag>/<value>")
def delete_tag(object_id: int, tag: str, value: str):
    metadata.remove_metadata(object_id, (tag, value))
    return good_response("Deleted")


@app.get("/obj/name/<name>")
def test_name(name: str):
    return good_response(metadata.get_object_id(name))


@app.get("/tags")
def tag_list():
    search = request.args.get("search", "")
    return good_response(metadata.get_metadata_keys(search))


@app.get("/tags/<tag>")
def tag_values(tag: str):
    search = request.args.get("search", "")
    return good_response(metadata.get_metadata_values(tag, search))
