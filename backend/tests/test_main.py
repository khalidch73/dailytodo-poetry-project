from fastapi.testclient import TestClient
from sqlmodel import Field, Session, SQLModel, create_engine, select
from myApp.main import app, get_session
from myApp import settings
from myApp.models import DailyTodo
from typing import Annotated, List

# 01 main rote test
def test_read_main():
    client = TestClient(app=app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_todo():
    
    connection_string = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")

    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        client = TestClient(app=app)

        todo_content = {
            "id": 1,
            "content": "This is a Pytest for create todo",
            "completed": False
        }

        response = client.post("/todos/", json=todo_content)
        data = response.json()

        assert response.status_code == 200
        assert data["content"] == todo_content["content"]

# 03 test for read_todo by id

def test_read_todo():
    # Override the database URL for testing
    connection_string = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")

    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    with Session(engine) as session:
        # Use the session provided by SQLModel for testing
        app.dependency_overrides[get_session] = lambda: session

        client = TestClient(app=app)

        # Assuming you have a todo_id available for testing
        todo_id = 1  # Change this to a valid todo_id for testing
        
        # Send GET request to read a todo by its id
        response = client.get(f"/todos/{todo_id}")
        
        # Check if the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Deserialize response to DailyTodo model
        retrieved_todo = DailyTodo(**response.json())
        
        # Check if the retrieved todo has the correct id
        assert retrieved_todo.id == todo_id

        # Clean up the database after the test
        session.rollback()  # Rollback the session to discard changes made during the test

# 04 test for read_all_todos

def test_read_all_todos():
    # Override the database URL for testing
    connection_string = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")

    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    with Session(engine) as session:
        # Use the session provided by SQLModel for testing
        app.dependency_overrides[get_session] = lambda: session

        client = TestClient(app=app)

        # Assuming you have some todos in the database for testing
        
        # Send GET request to read all todos
        response = client.get("/todos/")
        
        # Check if the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Deserialize response to list of DailyTodo models
        todos = [DailyTodo(**todo) for todo in response.json()]
        
        # Assuming you have assertions to make about the retrieved todos
        
        # For example, you can assert the length of the list
        assert len(todos) > 0

        # Clean up the database after the test
        session.rollback()  # Rollback the session to discard changes made during the test

# 05 test for update_todo

def test_update_todo():
    # Override the database URL for testing
    connection_string = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")

    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    with Session(engine) as session:
        # Use the session provided by SQLModel for testing
        app.dependency_overrides[get_session] = lambda: session

        client = TestClient(app=app)

        # Assuming you have some todos in the database for testing
        # For this test, let's assume you have a todo with ID 1
        
        # Send PUT request to update the todo with ID 1
        updated_todo_data = {"content": "Updated content", "completed": True}
        response = client.put("/todos/1", json=updated_todo_data)
        
        # Check if the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Check if the response contains the expected message
        assert response.json() == {"message": "Todo updated successfully"}
        
        # Check if the todo is updated in the database
        updated_todo = session.get(DailyTodo, 1)
        assert updated_todo.content == updated_todo_data["content"]
        assert updated_todo.completed == updated_todo_data["completed"]

        # Clean up the database after the test
        session.rollback()  # Rollback the session to discard changes made during the test


# 05 test for delete_todo

def test_delete_todo():
    # Override the database URL for testing
    connection_string = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")

    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    with Session(engine) as session:
        # Use the session provided by SQLModel for testing
        app.dependency_overrides[get_session] = lambda: session

        client = TestClient(app=app)

        # Assuming you have some todos in the database for testing
        # For this test, let's assume you have a todo with ID 1
        
        # Send DELETE request to delete the todo with ID 1
        response = client.delete("/todos/1")
        
        # Check if the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Check if the response contains the expected message
        assert response.json() == {"message": "Todo with ID 1 deleted successfully"}
        
        # Check if the todo is deleted from the database
        deleted_todo = session.get(DailyTodo, 1)
        assert deleted_todo is None

        # Clean up the database after the test
        session.rollback()  # Rollback the session to discard changes made during the test


# 06 test for delete_all_todos

def test_delete_all_todos():
    # Override the database URL for testing
    connection_string = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")

    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
    )

    with Session(engine) as session:
        # Use the session provided by SQLModel for testing
        app.dependency_overrides[get_session] = lambda: session

        client = TestClient(app=app)

        # Assuming you have some todos in the database for testing
        
        # Send DELETE request to delete all todos
        response = client.delete("/todos/")
        
        # Check if the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Check if the response contains the expected message
        assert response.json() == {"message": "All Todo items deleted successfully"}
        
        # Check if all todos are deleted from the database
        remaining_todos = session.query(DailyTodo).all()
        assert len(remaining_todos) == 0

        # Clean up the database after the test
        session.rollback()  # Rollback the session to discard changes made during the test