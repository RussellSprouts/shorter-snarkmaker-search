
import inspect
from typing import NewType, get_origin, get_args
from dataclasses import dataclass

Digest = NewType('Digest', int)

def converted_column():
    pass

def type_to_column(column_name, type):
    if type == int:
        if column_name == 'id':
            return f"{column_name} INTEGER PRIMARY KEY"
        return f"{column_name} INTEGER"
    elif type == Digest:
        return f"{column_name} INTEGER"
    elif type == str:
        return f"{column_name} TEXT"
    elif type == bytes:
        return f"{column_name} BLOB"
    elif type == float:
        return f"{column_name} REAL"
    elif get_origin(type) == tuple:
        print(get_args(type), get_args(type) == (MyClass2, Ellipsis))
        return "TUPLE UNKNOWN"
    elif get_origin(type) == list:
        (item_type,) = get_args(type)
        if not item_type.is_sqlite_table:
            raise TypeError(f"Type {item_type.__name__} is not a sqlite table.")
        return f"{column_name} INTEGER REFERENCES {item_type.__name__}(id)"
    else:
        return f"{column_name} INTEGER REFERENCES {type.__name__}(id)"

def table(cls):
    print(cls.__name__)
    print(cls.__dict__)
    print(inspect.get_annotations(cls))

    fields = [
        type_to_column(name, type)
        for name, type in inspect.get_annotations(cls).items()
    ]

    setattr(cls, 'create_statement', f"CREATE TABLE IF NOT EXISTS {cls.__name__} ({', '.join(fields)});")
    setattr(cls, 'is_sqlite_table', True)

    print(cls.create_statement)

    return cls

@table
@dataclass
class MyClass2:
    id: int
    a: int
    b: Digest

@table
@dataclass
class MyClass:
    a: list[MyClass2]
    b: tuple[MyClass2, ...]

print(MyClass.__annotations__['a'].__args__)