from sqlmodel import Field, SQLModel 

class DailyTodo(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True)
    content: str = Field(index=True)
    completed : bool = Field(default=False)
