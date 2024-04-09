# main.py
from contextlib import asynccontextmanager
from typing import Annotated, List
from myApp import settings 
from sqlmodel import Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends, HTTPException, Path
from myApp.models import DailyTodo


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    print("Tables created successfully")
    yield


app = FastAPI(lifespan=lifespan, title="Todo API", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

def get_session():
    with Session(engine) as session:
        yield session

# 01 Define the route to read route
@app.get("/")
def read_root():
    return {"Hello": "World"}

# 02 Define the route to create_todo Todos in database
@app.post("/todos/", response_model=DailyTodo)
def create_todo(todo: DailyTodo, session: Annotated[Session, Depends(get_session)]):
    existing_todo = session.get(DailyTodo, todo.id)
    if existing_todo:
        raise HTTPException(status_code=409, detail=f"Todo with ID {todo.id} already exists try another id")
    # Add the new todo item to the session
    session.add(todo)
    # Commit the transaction to save the changes to the database
    session.commit()
    # Refresh the todo item to ensure it reflects any changes made during the commit
    session.refresh(todo)
    # Return the created Todo item with its updated attributes.
    return todo

# 03 Define the route to read_todo by id in database
@app.get("/todos/{todo_id}", response_model=DailyTodo)
def read_todo(todo_id: int , session: Annotated[Session, Depends(get_session)]):
    # Retrieve the Todo item from the database based on the provided ID
    todo = session.get(DailyTodo, todo_id)
    if not todo:
        # If the Todo item with the provided ID doesn't exist, raise an HTTPException with status code 404 (Not Found)
        raise HTTPException(status_code=404, detail=f"Todo with ID {todo_id} not found.")
    # Return the retrieved Todo item
    return todo

# 04 Define the route to read_all_todos Todos in database
@app.get("/todos/", response_model=List[DailyTodo])
def read_all_todos(session: Annotated[Session, Depends(get_session)]):
    # Retrieve all Todo items from the database
    todos = session.query(DailyTodo).all()
    # Return the list of retrieved Todo items
    return todos

# 05 Define the route to delete_todo by id in database
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int , session: Annotated[Session, Depends(get_session)]):
    # Retrieve the Todo item from the database based on the provided ID
    todo = session.get(DailyTodo, todo_id)
    if not todo:
        # If the Todo item with the provided ID doesn't exist, raise an HTTPException with status code 404 (Not Found)
        raise HTTPException(status_code=404, detail=f"Todo with ID {todo_id} not found")
    # Delete the Todo item from the database
    session.delete(todo)
    # Commit the transaction to save the changes to the database
    session.commit()
    # Return a message indicating successful deletion
    return {"message": f"Todo with ID {todo_id} deleted successfully"}


# 06 Define the route to update_todo by id in database
@app.put("/todos/{todo_id}", response_model=DailyTodo)
def update_todo(todo_id: int, updated_todo: DailyTodo, session: Annotated[Session, Depends(get_session)]):
    # Retrieve the Todo item from the database based on the provided ID
    todo = session.get(DailyTodo, todo_id)
    if not todo:
        # If the Todo item with the provided ID doesn't exist, raise an HTTPException with status code 404 (Not Found)
        raise HTTPException(status_code=404, detail=f"Todo with ID {todo_id} not found")
    # Update the attributes of the Todo item with the provided data
    for key, value in updated_todo.dict().items():
        setattr(todo, key, value)
    # Commit the transaction to save the changes to the database
    session.commit()
    # Refresh the todo item to ensure it reflects any changes made during the commit
    session.refresh(todo)
    # Return a success message
    return {"message": "Todo updated successfully"}

# 07 Define the route to delete_all_todos in database
@app.delete("/todos/")
def delete_all_todos(session: Annotated[Session, Depends(get_session)]):
    # Retrieve all Todo items from the database
    todos = session.query(DailyTodo).all()
    if not todos:
        # If there are no Todo items in the database, return a message indicating that there are no items to delete
        raise HTTPException(status_code=404, detail="No Todo items found in the database")
    # Delete all Todo items from the database
    for todo in todos:
        session.delete(todo)
    # Commit the transaction to save the changes to the database
    session.commit()
    # Return a message indicating successful deletion
    return {"message": "All Todo items deleted successfully"}
