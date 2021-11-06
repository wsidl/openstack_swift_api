import sqlalchemy as sa
import dataclasses
import dotenv
import os
import typing

COL_OID = "o_id"
COL_OHASH = "o_hash"
COL_ONAME = "o_name"
COL_MKEY = "m_key"
COL_MVAL = "m_value"

dotenv.load_dotenv()
engine = sa.create_engine("postgresql://{u}:{w}@{h}:{p}/{d}".format(
    u=os.environ.get("PG_USER"),
    w=os.environ.get("PG_PASSWORD"),
    h=os.environ.get("PG_HOST", "127.0.0.1"),
    p=int(os.environ.get("PG_PORT", 5432)),
    d=os.environ.get("PG_DBNAME")
))
__meta = sa.MetaData()
_objects = sa.Table(
    "objects",
    __meta,
    sa.Column(COL_OID, sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(COL_OHASH, sa.String(40), unique=True),
    sa.Column(COL_ONAME, sa.Text)
)
_metadata = sa.Table(
    "metadata",
    __meta,
    sa.Column(COL_OID, sa.Integer, sa.ForeignKey("objects.o_id")),
    sa.Column(COL_MKEY, sa.String(50), index=True),
    sa.Column(COL_MVAL, sa.String(50)),
)
T_META_SET = tuple[str, str]


@dataclasses.dataclass
class Metadata:
    key: str
    value: str


@dataclasses.dataclass
class Object:
    id: int
    hash_string: str
    name: str
    _metadata: list[Metadata]

    def metadata(self, key: str = "") -> list[str]:
        return [m.value for m in self._metadata if not key or m.key == key]

    def all_metadata(self, key: str = "") -> list[[str, str]]:
        return [[m.key, m.value] for m in self._metadata if not key or key in m.key]


# Metadata Queries
def get_metadata_keys(search: str = "") -> list[str]:
    query = sa.select(_metadata.c.m_key)
    if search:
        query = query.where(_metadata.c.m_key.contains(search))
    query = query.group_by(_metadata.c.m_key)
    with engine.connect() as conn:
        return [row.m_key for row in conn.execute(query)]


def get_metadata_values(key: str, search: str = "") -> list[str]:
    query = sa.select(_metadata.c.m_value).where(_metadata.c.m_key == key)
    if search:
        query = query.where(_metadata.c.m_value.contains(search))
    query = query.group_by(_metadata.c.m_value)
    with engine.connect() as conn:
        return [row.m_value for row in conn.execute(query)]


def set_metadata(object_id: int, *metadata: T_META_SET) -> None:
    values = []
    for key, value in metadata:
        values.append({COL_OID: object_id, COL_MKEY: key, COL_MVAL: value})
    if not values:
        return
    with engine.connect() as conn:
        conn.execute(_metadata.insert(), values)


def remove_metadata(object_id: int, *metadata: T_META_SET) -> None:
    with engine.connect() as conn:
        for key, value in metadata:
            conn.execute(_metadata.delete().where(
                _metadata.c.o_id == object_id,
                _metadata.c.m_key == key,
                _metadata.c.m_value == value
            ))


# Object Queries
def add_object(object_name: str, hash_str: str, *metadata: T_META_SET) -> int:
    with engine.connect() as conn:
        o_id = conn.execute(
            _objects.insert(),
            {COL_ONAME: object_name, COL_OHASH: hash_str}
        ).inserted_primary_key[0]
        set_metadata(o_id, *metadata)
        return o_id


def remove_object(object_id: int) -> None:
    with engine.connect() as conn:
        conn.execute(_metadata.delete(_metadata.c.o_id == object_id))
        conn.execute(_objects.delete(_objects.c.o_id == object_id))


def get_object_id(object_name: str) -> typing.Optional[int]:
    query = sa.select(_objects.c.o_id).where(_objects.c.o_name == object_name)
    with engine.connect() as conn:
        row = conn.execute(query).fetchone()
        if row:
            return row.o_id
        return None


def find_object(search: str) -> list[int]:
    query = sa.select(_objects.c.o_id).where(_objects.c.o_name.contains(search))
    with engine.connect() as conn:
        return [o.o_id for o in conn.execute(query)]


def update_object_name(object_id: int, name: str):
    query = sa.update(_objects).where(_objects.c.o_id == object_id).values(o_name=name)
    with engine.connect() as conn:
        conn.execute(query)


def get_object(name_or_id: typing.Union[str, int]) -> Object:
    o_query = sa.select(_objects)
    m_query = sa.select(_metadata.c.m_key, _metadata.c.m_value)
    _id = get_object_id(name_or_id) if isinstance(name_or_id, str) else name_or_id

    o_query = o_query.where(_objects.c.o_id == _id)
    m_query = m_query.where(_metadata.c.o_id == _id)
    with engine.connect() as conn:
        obj = conn.execute(o_query).fetchone()
        return Object(
            obj.o_id, obj.o_hash, obj.o_name, [
                Metadata(m.m_key, m.m_value)
                for m in conn.execute(m_query)
            ]
        )
