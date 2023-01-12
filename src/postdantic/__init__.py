from pydantic import (
    BaseModel as PydanticBaseModel,
    Field,
    ConstrainedStr,
    ConstrainedInt,
    ConstrainedFloat,
    ConstrainedList,
)
from types import GenericAlias
from pydantic.fields import ModelField
from enum import Enum
from datetime import datetime


class ModelConfig:
    # orm_mode = True
    # allow_population_by_field_name = True
    arbitrary_types_allowed = True
    table_name: str = None


class PostgressFieldsTypes(Enum):
    TEXT = "TEXT"
    VARCHAR = "VARCHAR"
    CHAR = "CHAR"
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    NUMERIC = "NUMERIC"
    REAL = "REAL"
    DOUBLE_PRECISION = "DOUBLE PRECISION"
    SERIAL = "SERIAL"
    BIGSERIAL = "BIGSERIAL"
    MONEY = "MONEY"
    TIMESTAMP = "TIMESTAMP"
    TIMESTAMP_WITH_TIMEZONE = "TIMESTAMP WITH TIMEZONE"
    DATE = "DATE"
    BOOLEAN = "BOOLEAN"
    UUID = "UUID"


class cached_classproperty:
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        val = self.fget(owner_cls)
        setattr(owner_cls, self.fget.__name__, val)
        return val


class DBModel(PydanticBaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

    id: int

    @cached_classproperty
    def __table_name__(cls) -> str:
        name: str = cls.__name__

        for letter in name:

            if letter.isupper():

                name = name.replace(letter, f"_{letter.lower()}")

        name = name.replace("__", "_").replace("_", "", 1)

        return name

    @classmethod
    def generate_table_create_query(cls) -> str:

        create_sql = f"CREATE TABLE {cls.__table_name__} (id INTEGER PRIMARY KEY"

        model_fields = cls.__fields__

        for field_name, field in model_fields.items():
            if field_name == "id":
                continue

            create_sql += (
                f", {cls.format_field_for_sql_creation_table(field_name, field)}"
            )

        return create_sql + ");"

    @staticmethod
    def format_field_for_sql_creation_table(name: str, field: ModelField) -> str:

        field_type = field.outer_type_

        field_name = field.alias if field.has_alias else name

        # unlimited string length
        if field_type == str:
            field_type = "TEXT"
        elif issubclass(field_type, ConstrainedStr):
            if field.field_info.max_length == 1:
                field_type = "CHAR"
            else:
                field_type = f"VARCHAR({field.field_info.max_length})"
        elif field_type == int:
            field_type = "INTEGER"
        elif issubclass(field_type, ConstrainedInt):
            field_type = "INTEGER"
        elif field_type == float:
            field_type = "REAL"
        elif issubclass(field_type, ConstrainedFloat):
            field_type = "REAL"
        elif field_type == datetime:
            field_type = "TIMESTAMP"
        elif field_type == bool:
            field_type = "BOOLEAN"
        elif field_type == list:
            field_type = "JSONB"
        elif field_type == dict:
            field_type = "JSONB"
        elif (
            isinstance(field_type, GenericAlias) and field_type.__origin__ == list
        ) or issubclass(field_type, ConstrainedList):
            if field_type.__args__[0] == int:
                field_type = "INTEGER[]"
            elif field_type.__args__[0] == str:
                field_type = "VARCHAR[]"
            elif field_type.__args__[0] == float:
                field_type = "REAL[]"
            elif field_type.__args__[0] == datetime:
                field_type = "TIMESTAMP[]"
            elif field_type.__args__[0] == bool:
                field_type = "BOOLEAN[]"
            elif field_type.__args__[0] == dict:
                field_type = "JSONB"
            elif field_type.__args__[0] == list:
                field_type = "JSONB"
            else:
                raise ValueError(f"Type {field_type.__args__[0]} not supported")
        elif isinstance(field_type, GenericAlias) and field_type.__origin__ == dict:
            field_type = "JSONB"
        else:
            raise ValueError(f"Type {field_type} not supported")

        if field.required:
            field_type += " NOT NULL"

        return f"{field_name} {field_type}"


class TestModel(DBModel):
    name: str = Field(alias="full_name", max_length=100)
    age: int = Field(default=0)
    list_int: list[int] = Field(max_items=10)
    dict_: dict[str, str] = Field()


print(TestModel.generate_table_create_query())
