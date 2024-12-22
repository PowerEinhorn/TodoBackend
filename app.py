import json
import os.path

from fastapi import FastAPI
import datetime

from fastapi import Response

app = FastAPI()

from pydantic import BaseModel


class Todo(BaseModel):
    name: str
    description: str | None = None
    deadline: datetime.datetime | None = None


class TodoDTO(BaseModel):
    id: int
    created_at: datetime.datetime

    name: str
    description: str | None = None
    deadline: datetime.datetime | None = None

    def to_json(self):
        return {
            "id": self.id,
            "created_at": str(self.created_at),
            "name": self.name,
            "description": self.description,
            "deadline": str(self.deadline)
        }


if os.path.exists("db.json"):
    db: dict[int, TodoDTO] = json.load(open("db.json"))

    db = {k: TodoDTO(**v) for k, v in db.items()}
else:
    db: dict[int, TodoDTO] = {}
max_id = 0


@app.post("/todo/")
async def create_todo(todo: Todo) -> TodoDTO:
    global max_id
    dto = TodoDTO(
        id=max_id + 1,
        created_at=datetime.datetime.now(),
        name=todo.name,
        description=todo.description,
        deadline=todo.deadline
    )

    db[dto.id] = dto

    json.dump({k: v.to_json() for k, v in db.items()}, open("db.json", "w"), indent=4)
    max_id += 1

    return dto


@app.get("/todo")
async def get_todos() -> list[TodoDTO]:
    return list(db.values())


@app.get("/todo/{todo_id}")
async def read_item(todo_id):
    if db.get(todo_id) != None:
        return db[todo_id]
    else:
        return Response(status_code=404, content="<h1>404</h1>")


@app.put("/todo/{todo_id}")
async def put_item(todo_id, todo: Todo):
    dto = db.get(todo_id)
    if dto is None:
        return Response(status_code=404, content="<h1>Der Gesuchte Pfosten wurde nicht gefunden</h1>")

    dto.name = todo.name
    dto.description = todo.description
    dto.deadline = todo.deadline

    json.dump({k: v.to_json() for k, v in db.items()}, open("db.json", "w"), indent=4)

    return dto


@app.delete("/todo/{todo_id}")
async def delete_item(todo_id):
    dto = db.get(todo_id)
    if dto is None:
        return Response(status_code=404, content="<h1>Der Gesuchte Pfosten wurde nicht gefunden</h1>")

    db.pop(todo_id)

    json.dump({k: v.to_json() for k, v in db.items()}, open("db.json", "w"), indent=4)
