from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:8000",
    "localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TodoItem(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="ID")
    title: str
    completed: bool = False

todos = {}

@app.post('/createtask', response_model=TodoItem)
def post_todo(todo: TodoItem) -> dict:
    todos[todo.id] = todo
    return {"msg": "Todo has been added", "data": todo}

@app.get('/todos', response_model=list[TodoItem])
def get_all_todos():
    return list(todos.values())

@app.get('/todos/{id}', response_model=TodoItem)
def get_todo(id: UUID):
    todo = todos.get(id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.get("/todos/title/{title}", response_model=TodoItem)
def get_todo_by_title(title: str):
    for todo in todos.values():
        if todo.title == title:
            return todo
    raise HTTPException(status_code=404, detail="Todo with title not found")

@app.delete("/todos/delete/title/{title}")
async def delete_todo_by_title(title: str):
    deleted = False
    for todo_id, todo in list(todos.items()):
        if todo.title == title:
            del todos[todo_id]
            deleted = True
    if deleted:
        return {"msg": f"Todos with title '{title}' have been deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"No todos with title '{title}' found")

@app.delete("/todos/delete/all")
async def delete_all_todos():
    todos.clear()
    return {"msg": "All todos have been deleted successfully"}

@app.put("/todos/edit/{id}", response_model=TodoItem)
async def update_todo(id: UUID, title: Optional[str] = None, completed: Optional[bool] = None):
    todo = todos.get(id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if title is not None:
        todo.title = title
    if completed is not None:
        todo.completed = completed

    return todo

@app.delete("/todos/delete/{id}")
async def delete_todo(id: UUID):
    if id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos[id]
    return {"msg": "Todo has been deleted successfully"}
