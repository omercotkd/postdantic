from pydantic import (
    BaseModel as PydanticBaseModel,
    ConstrainedStr,
    ConstrainedInt,
    ConstrainedFloat,
    ConstrainedList,
)
from typing import Type
from functools import cached_property
from pydantic.fields import ModelField
from pydantic.typing import is_literal_type
from types import GenericAlias
from datetime import datetime


class ModelHelper:
    """
    A class that helps using pydantic models with postgreSQL.
    """
    def __init__(self, model: Type[PydanticBaseModel], table_name: str = None):
        """
        params:
            model: a pydantic model
            table_name: name of the table in the database if not provided a snake case version of the model name will be used
        """
        if not issubclass(model, PydanticBaseModel):
            raise TypeError("model must be a subclass of Pydantic BaseModel")
        if not model.__fields__:
            raise ValueError("model must have fields")
        if table_name and not isinstance(table_name, str):
            raise TypeError("table_name must be a string")

        self.__model = model
        self.__table_name = table_name

    @cached_property
    def table_name(self) -> str:

        if self.__table_name:
            return self.__table_name

        name = self.__model.__name__

        for letter in name:

            if letter.isupper():

                name = name.replace(letter, f"_{letter.lower()}")

        name = name.replace("__", "_").replace("_", "", 1)

        return name

    @cached_property
    def create_table_string(self) -> str:

        create_sql = f"CREATE TABLE {self.table_name} ("

        model_fields = self.__model.__fields__

        for field_name, field in model_fields.items():
            create_sql += (
                f"{self.format_field_to_sql(field_name, field)}, "
            )

        create_sql = create_sql[:-2]

        return create_sql + ");"

    def format_field_to_sql(self, name: str, field: ModelField) -> str:

        field_type = field.outer_type_

        field_name = field.alias if field.has_alias else name

        field_definition: list[str] = [field_name]


        # add to the field definition the type of the field
        if field_type == str:
            field_definition.append("TEXT")
        elif is_literal_type(field_type):
            raise NotImplementedError("Literal types are not supported yet")
        elif issubclass(field_type, ConstrainedStr):
            if field.field_info.max_length == 1:
                field_definition.append("CHAR")
            else:
                field_definition.append(f"VARCHAR({field.field_info.max_length})")
        elif field_type == int or issubclass(field_type, ConstrainedInt):
            field_definition.append("INTEGER")
        elif field_type == float or issubclass(field_type, ConstrainedFloat):
            field_definition.append("REAL")
        elif field_type == datetime:
            field_definition.append("TIMESTAMP")
        elif field_type == bool:
            field_definition.append("BOOLEAN")
        elif field_type == list:
            field_definition.append("JSONB")
        elif field_type == dict:
            field_definition.append("JSONB")
        elif (
            isinstance(field_type, GenericAlias) and field_type.__origin__ == list
        ) or issubclass(field_type, ConstrainedList):
            if field_type.__args__[0] == int:
                field_definition.append("INTEGER[]")
            elif field_type.__args__[0] == str:
                field_definition.append("VARCHAR[]")
            elif field_type.__args__[0] == float:
                field_definition.append("REAL[]")
            elif field_type.__args__[0] == datetime:
                field_definition.append("TIMESTAMP[]")
            elif field_type.__args__[0] == bool:
                field_definition.append("BOOLEAN[]")
            elif field_type.__args__[0] == dict:
                field_definition.append("JSONB[]")
            elif field_type.__args__[0] == list:
                field_definition.append("JSONB[]")
            elif issubclass(field_type.__args__[0], PydanticBaseModel):
                field_definition.append("JSONB[]")
            else:
                raise ValueError(f"Type {field_type.__args__[0]} not supported")
        elif isinstance(field_type, GenericAlias) and field_type.__origin__ == dict:
            field_definition.append("JSONB")
        elif issubclass(field_type, PydanticBaseModel):
            field_definition.append("JSONB")
        else:
            raise ValueError(f"Type {field_type} not supported")

        if field.required:
            field_definition.append("NOT NULL")

        if field.default:
            field_definition.append(f"DEFAULT {field.default}")

        if field.field_info.extra.get("primary_key"):
            field_definition.append("PRIMARY KEY GENERATED ALWAYS AS IDENTITY")
        
        if field.field_info.extra.get("unique"):
            field_definition.append("UNIQUE")

        return " ".join(field_definition)
