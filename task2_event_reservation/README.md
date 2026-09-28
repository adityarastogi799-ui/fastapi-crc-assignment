# Task 2: Campus Event Seat Reservation API

## Short Description
A simple FastAPI application to manage campus events and seat reservations. It allows organizers to create and manage events, check seat availability, and allows students to reserve seats or cancel reservations.

## Technologies
- Python
- FastAPI
- SQLModel
- SQLite
- Uvicorn

## How to Install Requirements
Run the following command in the `task2_event_reservation` directory:
```bash
pip install -r requirements.txt
```

## How to Run the Project
Navigate to the `task2_event_reservation` folder and start the server:
```bash
uvicorn main:app --reload
```

## Swagger URL
Interactive API documentation is available at:
`http://127.0.0.1:8000/docs`

## API Endpoint List
- `POST /events` - Create a new event
- `GET /events` - Get all events
- `GET /events/{event_id}` - Get single event by ID
- `PUT /events/{event_id}` - Update event details
- `DELETE /events/{event_id}` - Delete an event by ID
- `POST /events/{event_id}/reserve` - Reserve a seat for an event
- `GET /events/{event_id}/reservations` - Get all reservations for an event
- `DELETE /reservations/{reservation_id}` - Cancel a reservation by ID
- `GET /events/{event_id}/availability` - Check event seat availability (capacity, booked, remaining)
