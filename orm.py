from typing import NewType, get_origin, get_args
from dataclasses import dataclass
from annotationlib import ForwardRef, get_annotations, Format

# Digests are 64 bit ints. In Python they are unsigned, but
# sqlite only supports signed 64 bit, so we must convert.
Digest = NewType("Digest", int)
PrimaryKey = NewType("PrimaryKey", int)


def assert_can_be_foreign_key(cls):
    if not hasattr(cls, "orm_metadata"):
        raise TypeError(f"Type {cls.__tablename__} is not a sqlite table")


def type_to_column(column_name, type):
    if type == int:
        return f"{column_name} INTEGER"
    elif type == str:
        return f"{column_name} TEXT"
    elif type == bytes:
        return f"{column_name} BLOB"
    elif type == float:
        return f"{column_name} REAL"
    elif type == PrimaryKey:
        return f"{column_name} INTEGER PRIMARY KEY"
    elif type == Digest:
        return f"{column_name} INTEGER"
    elif isinstance(type, ForwardRef):
        print("Found a forwardref!", type)
        return "TODO"
    elif get_origin(type) == tuple:
        # TODO the other table should reference this by id.
        item_type, ellipsis = get_args(type)
        if ellipsis != Ellipsis:
            raise TypeError("Tuples must be of a single type.")
        assert_can_be_foreign_key(item_type)
        return f"{column_name} INTEGER REFERENCES {item_type.__tablename__}(id)"
    elif get_origin(type) == list:
        # TODO the other table should reference this by id.
        (item_type,) = get_args(type)
        assert_can_be_foreign_key(item_type)
        return f"{column_name} INTEGER REFERENCES {item_type.__tablename__}(id)"
    else:
        assert_can_be_foreign_key(type)
        return f"{column_name} INTEGER REFERENCES {type.__tablename__}(id)"


@dataclass
class OrmMetadata:
    in_memory: bool
    create_statement: str


def table(cls=None, *, in_memory=False):
    if not cls:

        def annotation(cls):
            return table(cls, in_memory=in_memory)

        return annotation

    fields = [
        type_to_column(name, type)
        for name, type in get_annotations(cls, format=Format.FORWARDREF).items()
    ]

    setattr(
        cls,
        "orm_metadata",
        OrmMetadata(
            in_memory=in_memory,
            create_statement=f"CREATE TABLE IF NOT EXISTS {cls.__tablename__} ({', '.join(fields)});",
        ),
    )

    print(cls.orm_metadata.create_statement)

    return cls


@table
@dataclass
class StartingPoint:
    __tablename__ = "starting_points"

    id: int
    stream: bytes

@table(in_memory=True)
@dataclass
class RecipeIntermediate:
    id: PrimaryKey
    so_far: bytes
    remaining: bytes
    rle_string: str


@table
@dataclass
class IntermediateMatch:
    __tablename__ = "intermediate_matches"

    percent: float
    result: Result


@table
@dataclass
class Result:
    __tablename__ = "results"

    id: PrimaryKey
    a: int
    b: Digest
    starting_point: StartingPoint
    intermediate_matches: list[IntermediateMatch]
