from src.postdantic import ModelHelper
from pydantic import BaseModel, Field


class MiniTests(BaseModel):
    name: str = Field(alias="full_name", max_length=100, unique=True)
    age: int = Field(default=0)


class TestModel(BaseModel):
    id: int = Field(primary_key=True)
    name: str = Field(alias="full_name", max_length=100, unique=True)
    age: int = Field(default=0)
    list_int: list[int] = Field(max_items=10)
    dict_: dict[str, str] = Field()
    list_tests: list[MiniTests] = Field(max_items=10)



test_helper = ModelHelper(TestModel)

print(test_helper.create_table_string)