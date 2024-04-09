from fastapi.testclient import TestClient
from sqlmodel import Field, Session, SQLModel, create_engine, select
from myApp.main import app, get_session
from myApp import settings


def test_read_main():
    client = TestClient(app=app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_write_main():

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

        todo_content = "buy bread"

        response = client.post("/todos/",
            json={"content": todo_content}
        )

        data = response.json()

        assert response.status_code == 200
        assert data["content"] == todo_content


def test_create_todo():
    client = TestClient(app=app)

    # Sample todo data
    todo_data = {
        "id": 10,
        "content": "Buy groceries",
        "completed": False
    }

    # Send a POST request to create the todo
    response = client.post("/todos/", json=todo_data)

    # Check if the response status code is 200
    assert response.status_code == 200

    # Check if the response JSON contains the expected todo content
    assert response.json() == todo_data