# because sqlModel is based on sqlAlchamy and pydantic so sqlModel work both for dataValidation and table creation because 
from sqlmodel import Field, SQLModel   

class DailyTodo(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True)
    content: str = Field(index=True, min_length=1, max_length=255)
    completed : bool = Field(default=False)
