# Campus Management REST API — CRC Assessment

A production-ready FastAPI application built for college campus administration, encompassing **Task 1: Campus Lost & Found System** and **Task 2: Campus Event Seat Reservation System** using **SQLite** and **SQLModel**.

---

## 1. Project Description

This repository provides two complete RESTful micro-services designed for campus student services:

1. **Campus Lost & Found API (Task 1)**:
   A centralized system allowing students and campus security to register, query, update, and manage lost or found items with strict status validation (`Lost`, `Found`, `Returned`) and categorization.
2. **Campus Event Seat Reservation API (Task 2)**:
   A seat reservation platform for campus workshops, seminars, and hackathons. It prevents overbooking by actively tracking capacity, prevents reservations for closed events, and provides real-time seat availability.

---

## 2. Technologies Used

- **Language**: Python 3.13+ / 3.14
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (High performance, async-ready, auto-generating OpenAPI docs)
- **ORM / Data Modeling**: [SQLModel](https://sqlmodel.tiangolo.com/) (Combines SQLAlchemy and Pydantic)
- **Database**: SQLite
- **Validation**: Pydantic v2 & `email-validator`
- **ASGI Server**: Uvicorn
- **Testing**: FastAPI TestClient & Pytest / Requests

---

## 3. Installation Steps

### Prerequisites
- Python 3.13 or higher installed.

### Option A: Using `pip` and Virtual Environment
```bash
# 1. Clone repository
git clone <YOUR_REPOSITORY_URL>
cd fastapi-CRC

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Option B: Using `uv` (Fast Package Manager)
```bash
uv sync
```

---

## 4. Command to Run the FastAPI Application

From the project root directory, run:

```bash
uvicorn main:app --reload
```
or with FastAPI CLI:
```bash
fastapi dev main.py
```

The server will start at: `http://127.0.0.1:8000`

---

## 5. Swagger UI & Documentation URLs

- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema (JSON)**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 6. Brief Description of Available Endpoints

### Task 1 — Campus Lost & Found API (`/items`)

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `POST` | `/items` | Register a new lost/found item | `201 Created` |
| `GET` | `/items` | Retrieve all reported items | `200 OK` |
| `GET` | `/items/{item_id}` | Retrieve item by ID (returns 404 if not found) | `200 OK` |
| `PUT` | `/items/{item_id}` | Update item details or status (returns 404 if not found) | `200 OK` |
| `DELETE` | `/items/{item_id}` | Delete item report (returns 404 if not found) | `200 OK` |
| `GET` | `/items/status/{status}` | Filter items by status (`Lost`, `Found`, `Returned`) | `200 OK` / `400 Bad Request` |
| `GET` | `/items/category/{category}` | Filter items by category (case-insensitive) | `200 OK` |

### Task 2 — Campus Event Seat Reservation API (`/events` & `/reservations`)

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `POST` | `/events` | Create a new campus event (capacity > 0) | `201 Created` |
| `GET` | `/events` | Retrieve all campus events | `200 OK` |
| `GET` | `/events/{event_id}` | Retrieve specific event details (returns 404 if not found) | `200 OK` |
| `PUT` | `/events/{event_id}` | Update event details (capacity, venue, status) | `200 OK` |
| `DELETE` | `/events/{event_id}` | Delete an event and its reservations | `200 OK` |
| `POST` | `/events/{event_id}/reserve` | Reserve a seat (verifies event exists, Open status, & capacity) | `201 Created` / `400 Bad Request` |
| `GET` | `/events/{event_id}/reservations` | Retrieve all student reservations for an event | `200 OK` |
| `GET` | `/events/{event_id}/availability` | Get seat availability (`capacity`, `booked`, `remaining`) | `200 OK` |
| `DELETE` | `/reservations/{reservation_id}` | Cancel a student reservation | `200 OK` |

---

## 7. Task 1 — Application Logic Explanation

### 1. How the SQLite database is created using `create_engine()`
In `app/database.py`, SQLAlchemy's `create_engine()` is called with the database connection URL `sqlite:///campus.db`:
```python
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)
```
- `sqlite:///campus.db` specifies the local SQLite file.
- `connect_args={"check_same_thread": False}` is required by SQLite in FastAPI because multiple threads may handle incoming HTTP requests concurrently.
- On startup, the FastAPI `lifespan` context manager calls `SQLModel.metadata.create_all(bind=engine)`, which inspects all models defined with `table=True` and generates the corresponding SQLite tables if they do not already exist.

### 2. How SQLModel is used to store and retrieve items
- **Storing**: Incoming JSON request data is validated against the `ItemCreate` schema. `Item.model_validate(item_in.model_dump())` converts the payload into an `Item` table model instance. It is added to the database session using `session.add(item)`, persisted to SQLite via `session.commit()`, and refreshed with `session.refresh(item)` to populate the auto-generated primary key `id`.
- **Retrieving**: Queries are constructed using SQLModel's `select(Item)`. Using `session.exec(statement).all()`, SQLModel executes the SQL query against SQLite and automatically maps the returned rows into typed Python `Item` instances.

### 3. How you implemented status/category filtering
- **Status Filtering (`GET /items/status/{status}`)**: The endpoint checks the path parameter against valid statuses defined in the `ItemStatus` enum (`Lost`, `Found`, `Returned`). If valid, it executes `select(Item).where(Item.status == matched_status)`. If invalid, an `HTTPException(status_code=400)` is raised with a descriptive message.
- **Category Filtering (`GET /items/category/{category}`)**: Uses `select(Item).where(func.lower(Item.category) == category.strip().lower())` to filter items case-insensitively.

### 4. How your API handles a non-existing item ID
Whenever an endpoint receives an `item_id`, it queries SQLite using `session.get(Item, item_id)`. If the return value is `None`, the API immediately raises:
```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Item with ID {item_id} not found",
)
```
FastAPI translates this into a standard JSON 404 response body: `{"detail": "Item with ID <id> not found"}`.

### 5. How validation prevents invalid status values
- Status is defined as an Enum `ItemStatus(str, Enum)` with values `Lost`, `Found`, and `Returned`.
- In Pydantic/SQLModel schemas, `status: ItemStatus` enforces that any POST or PUT payload containing a status value outside these three options is automatically rejected with an HTTP `422 Unprocessable Entity` status code before touching the database.
- Path parameter filtering also performs normalization and validation, returning HTTP `400 Bad Request` if an invalid status is passed.

---

## 8. Task 2 — Application Logic Explanation

### 1. How you check whether an event exists before creating a reservation
Before accepting a reservation in `POST /events/{event_id}/reserve`, the API executes `session.get(Event, event_id)`. If the returned object is `None`, the API raises an `HTTPException(status_code=404, detail="Event with ID <event_id> not found")`, halting execution before creating any reservation record.

### 2. How you calculate booked and remaining seats
Seat availability is computed dynamically from the database using SQL aggregate functions:
```python
count_statement = select(func.count(Reservation.id)).where(Reservation.event_id == event_id)
booked_count = session.exec(count_statement).one()
remaining = max(0, event.capacity - booked_count)
```
The endpoint returns:
```json
{
  "capacity": event.capacity,
  "booked": booked_count,
  "remaining": remaining
}
```

### 3. How you prevent overbooking
Before saving a new reservation, the API counts current reservations for the target event:
```python
if booked_count >= event.capacity:
    raise HTTPException(
        status_code=400,
        detail=f"Cannot reserve seat: Event is already fully booked ({booked_count}/{event.capacity} seats taken)"
    )
```
If the event is already full, the request is rejected with HTTP `400 Bad Request`.

### 4. How you prevent reservations for closed events
The `Event` model contains a `status` field (`EventStatus.OPEN` or `EventStatus.CLOSED`). In the reservation route, the API checks:
```python
if event.status != EventStatus.OPEN:
    raise HTTPException(
        status_code=400,
        detail="Cannot reserve seat: This event is Closed for registrations"
    )
```
If the event status is `Closed`, reservations are prohibited and rejected with HTTP `400 Bad Request`.

### 5. How SQLModel Session is used to perform database operations
FastAPI's dependency injection (`Depends(get_session)`) yields a context-managed `Session(engine)`:
- `session.add(instance)`: Stages new or modified objects in the session.
- `session.commit()`: Commits the active transaction to disk in SQLite.
- `session.refresh(instance)`: Refreshes object attributes from the database (e.g. Generated IDs).
- `session.get(Model, id)`: Fetches an entity by primary key.
- `session.exec(statement)`: Executes SQLModel `select()` queries.
- `session.delete(instance)`: Marks an entity for deletion.
- When the request completes, the `with` block automatically closes the session, preventing database connection leaks.

---

## 9. Challenges Faced / Additional Comments

- **SQLite Multi-Threading Concurrency**: In FastAPI, path operation functions may run across different threads. SQLite by default restricts connections to the creating thread. This was resolved by passing `connect_args={"check_same_thread": False}` into `create_engine()`.
- **Foreign Key Constraint Integrity**: Deleting an event that has active reservations could leave orphaned rows. In `delete_event()`, cascading deletion of related reservations was explicitly handled in the session before deleting the event itself.
- **Strict Input Sanitization**: Standard string validation could allow whitespace-only inputs (`"   "`). Custom Pydantic `@field_validator` hooks were added to strip and enforce non-empty character lengths on titles, descriptions, and student details.

---

## 10. Proof of Work (Screenshots)

All proof-of-work images are located in the `screenshots/` directory:

| Screenshot | Scenario | Endpoint |
|---|---|---|
| `task1_01_post_item.png` | Create item | `POST /items` |
| `task1_02_get_all_items.png` | Get all items | `GET /items` |
| `task1_03_get_item_by_id.png` | Get item by ID | `GET /items/{id}` |
| `task1_04_put_update_item.png` | Update item details/status | `PUT /items/{id}` |
| `task1_05_get_items_by_status.png` | Status filtering | `GET /items/status/{status}` |
| `task1_06_get_items_by_category.png` | Category filtering | `GET /items/category/{category}` |
| `task1_07_delete_item.png` | Delete item | `DELETE /items/{id}` |
| `task1_08_invalid_request_validation_error.png` | Validation error (Invalid status) | `POST /items` (422) |
| `task2_01_post_event.png` | Create event | `POST /events` |
| `task2_02_get_all_events.png` | Get all events | `GET /events` |
| `task2_03_get_event_availability.png` | Event availability | `GET /events/{id}/availability` |
| `task2_04_successful_reservation_creation.png` | Seat reservation | `POST /events/{id}/reserve` |
| `task2_05_get_event_reservations.png` | Event reservations list | `GET /events/{id}/reservations` |
| `task2_06_unsuccessful_reservation_full_event.png` | Overbooking prevention | `POST /events/{id}/reserve` (400) |
| `task2_07_successful_reservation_cancellation.png` | Cancel reservation | `DELETE /reservations/{id}` |
