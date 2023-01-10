from pydantic import BaseModel as PydanticBaseModel, Field, ConstrainedStr
from pydantic.fields import ModelField

class ModelConfig:
    # orm_mode = True
    # allow_population_by_field_name = True
    arbitrary_types_allowed = True
    table_name: str = None


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

        create_sql = f"CREATE TABLE {cls.__table_name__} (id INTEGER PRIMARY KEY)"

        model_fields = cls.__fields__

        for field_name, field in model_fields.items():
                
            if field_name == "id":
                continue

            create_sql += f", {cls.format_field_for_sql_creation_table(field_name, field)}"

        return create_sql
        
    @classmethod
    def format_field_for_sql_creation_table(cls, name: str, field: ModelField) -> str:

        field_type = field.type_

        field_name = field.alias or name
  
        # unlimited string length
        if field_type == str:
            field_type = "TEXT"
        elif issubclass(field_type, ConstrainedStr):
            field_type = f"VARCHAR({field.field_info.max_length})"
        
        if field.required:
            field_type += " NOT NULL"

        return f"{field_name} {field_type}"
        

class TestModel(DBModel):
    name: str = Field(alias="full_name", max_length=100)
    age: int = Field(default=0)


print(TestModel.generate_table_create_query())
