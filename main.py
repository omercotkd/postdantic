from src.postdantic import ModelHelper
from pydantic import BaseModel, Field



class TestModel(BaseModel):
    id: int = Field(primary_key=True)
    name: str = Field(alias="full_name", max_length=100, unique=True)
    age: int = Field(default=0)
    list_int: list[int] = Field(max_items=10)
    dict_: dict[str, str] = Field()


# how to get all the fields and thier attributes from the model


test_helper = ModelHelper(TestModel)

print(test_helper.create_table_string)