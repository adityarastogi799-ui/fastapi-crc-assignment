# Task 1: Campus Lost & Found API

## Short Description
A simple FastAPI application to manage lost and found items on campus. It allows users to report lost or found items, view items, search by category or status, update item details, and delete items.

## Technologies
- Python
- FastAPI
- SQLModel
- SQLite
- Uvicorn

## How to Install Requirements
Run the following command in the `task1_lost_found` directory:
```bash
pip install -r requirements.txt
```

## How to Run the Project
Navigate to the `task1_lost_found` folder and start the server:
```bash
uvicorn main:app --reload
```

## Swagger URL
Interactive API documentation is available at:
`http://127.0.0.1:8000/docs`

## API Endpoint List
- `POST /items` - Create a lost or found item
- `GET /items` - Retrieve all items
- `GET /items/{item_id}` - Retrieve a single item by ID
- `PUT /items/{item_id}` - Update an item by ID
- `DELETE /items/{item_id}` - Delete an item by ID
- `GET /items/status/{status}` - Get items filtered by status (`Lost`, `Found`, `Returned`)
- `GET /items/category/{category}` - Get items filtered by category
