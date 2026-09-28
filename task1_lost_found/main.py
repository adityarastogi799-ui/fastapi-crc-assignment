from typing import Optional, List
from fastapi import FastAPI, HTTPException
from sqlmodel import Field, SQLModel, create_engine, Session, select

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    category: str
    location: str
    reported_by: str
    status: str

database_url = "sqlite:///assignment.db"
engine = create_engine(database_url, connect_args={"check_same_thread": False})

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/items", response_model=Item)
def create_item(item: Item):
    if not item.title or not item.title.strip():
        raise HTTPException(status_code=400, detail="Title should not be empty")
    if not item.description or not item.description.strip():
        raise HTTPException(status_code=400, detail="Description should not be empty")
    if not item.category or not item.category.strip():
        raise HTTPException(status_code=400, detail="Category should not be empty")
    if not item.location or not item.location.strip():
        raise HTTPException(status_code=400, detail="Location should not be empty")
    if not item.reported_by or not item.reported_by.strip():
        raise HTTPException(status_code=400, detail="Reported by should not be empty")
    if item.status not in ["Lost", "Found", "Returned"]:
        raise HTTPException(status_code=400, detail="Status must be Lost, Found, or Returned")
    
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

@app.get("/items", response_model=List[Item])
def get_all_items():
    with Session(engine) as session:
        items = session.exec(select(Item)).all()
        return items

@app.get("/items/status/{status}", response_model=List[Item])
def get_items_by_status(status: str):
    if status not in ["Lost", "Found", "Returned"]:
        raise HTTPException(status_code=400, detail="Status must be Lost, Found, or Returned")
    with Session(engine) as session:
        items = session.exec(select(Item).where(Item.status == status)).all()
        return items

@app.get("/items/category/{category}", response_model=List[Item])
def get_items_by_category(category: str):
    with Session(engine) as session:
        items = session.exec(select(Item).where(Item.category == category)).all()
        return items

@app.get("/items/{item_id}", response_model=Item)
def get_one_item(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item):
    if not updated_item.title or not updated_item.title.strip():
        raise HTTPException(status_code=400, detail="Title should not be empty")
    if not updated_item.description or not updated_item.description.strip():
        raise HTTPException(status_code=400, detail="Description should not be empty")
    if not updated_item.category or not updated_item.category.strip():
        raise HTTPException(status_code=400, detail="Category should not be empty")
    if not updated_item.location or not updated_item.location.strip():
        raise HTTPException(status_code=400, detail="Location should not be empty")
    if not updated_item.reported_by or not updated_item.reported_by.strip():
        raise HTTPException(status_code=400, detail="Reported by should not be empty")
    if updated_item.status not in ["Lost", "Found", "Returned"]:
        raise HTTPException(status_code=400, detail="Status must be Lost, Found, or Returned")

    with Session(engine) as session:
        db_item = session.get(Item, item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        db_item.title = updated_item.title
        db_item.description = updated_item.description
        db_item.category = updated_item.category
        db_item.location = updated_item.location
        db_item.reported_by = updated_item.reported_by
        db_item.status = updated_item.status
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        session.delete(item)
        session.commit()
        return {"message": "Item deleted successfully"}
