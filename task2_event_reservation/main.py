from typing import Optional, List
from fastapi import FastAPI, HTTPException
from sqlmodel import Field, SQLModel, create_engine, Session, select

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    venue: str
    capacity: int
    organizer: str
    status: str

class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int
    student_name: str
    roll_number: str
    email: str

database_url = "sqlite:///assignment.db"
engine = create_engine(database_url, connect_args={"check_same_thread": False})

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/events", response_model=Event)
def create_event(event: Event):
    if not event.title or not event.title.strip():
        raise HTTPException(status_code=400, detail="Title should not be empty")
    if not event.venue or not event.venue.strip():
        raise HTTPException(status_code=400, detail="Venue should not be empty")
    if event.capacity <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be greater than 0")
    if not event.organizer or not event.organizer.strip():
        raise HTTPException(status_code=400, detail="Organizer should not be empty")
    if event.status not in ["Open", "Closed"]:
        raise HTTPException(status_code=400, detail="Status must be Open or Closed")

    with Session(engine) as session:
        session.add(event)
        session.commit()
        session.refresh(event)
        return event

@app.get("/events", response_model=List[Event])
def get_all_events():
    with Session(engine) as session:
        events = session.exec(select(Event)).all()
        return events

@app.get("/events/{event_id}", response_model=Event)
def get_one_event(event_id: int):
    with Session(engine) as session:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event

@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: int, updated_event: Event):
    if not updated_event.title or not updated_event.title.strip():
        raise HTTPException(status_code=400, detail="Title should not be empty")
    if not updated_event.venue or not updated_event.venue.strip():
        raise HTTPException(status_code=400, detail="Venue should not be empty")
    if updated_event.capacity <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be greater than 0")
    if not updated_event.organizer or not updated_event.organizer.strip():
        raise HTTPException(status_code=400, detail="Organizer should not be empty")
    if updated_event.status not in ["Open", "Closed"]:
        raise HTTPException(status_code=400, detail="Status must be Open or Closed")

    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        db_event.title = updated_event.title
        db_event.venue = updated_event.venue
        db_event.capacity = updated_event.capacity
        db_event.organizer = updated_event.organizer
        db_event.status = updated_event.status
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        return db_event

@app.delete("/events/{event_id}")
def delete_event(event_id: int):
    with Session(engine) as session:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        session.delete(event)
        session.commit()
        return {"message": "Event deleted successfully"}

@app.post("/events/{event_id}/reserve", response_model=Reservation)
def reserve_seat(event_id: int, reservation: Reservation):
    reservation.event_id = event_id
    if not reservation.student_name or not reservation.student_name.strip():
        raise HTTPException(status_code=400, detail="Student name should not be empty")
    if not reservation.roll_number or not reservation.roll_number.strip():
        raise HTTPException(status_code=400, detail="Roll number is required")
    if not reservation.email or "@" not in reservation.email or "." not in reservation.email:
        raise HTTPException(status_code=400, detail="Email should be valid")

    with Session(engine) as session:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        if event.status != "Open":
            raise HTTPException(status_code=400, detail="Closed events cannot accept reservations")

        existing_reservations = session.exec(select(Reservation).where(Reservation.event_id == event_id)).all()
        if len(existing_reservations) >= event.capacity:
            raise HTTPException(status_code=400, detail="Event is full")

        session.add(reservation)
        session.commit()
        session.refresh(reservation)
        return reservation

@app.get("/events/{event_id}/reservations", response_model=List[Reservation])
def get_event_reservations(event_id: int):
    with Session(engine) as session:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        reservations = session.exec(select(Reservation).where(Reservation.event_id == event_id)).all()
        return reservations

@app.delete("/reservations/{reservation_id}")
def cancel_reservation(reservation_id: int):
    with Session(engine) as session:
        reservation = session.get(Reservation, reservation_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")
        session.delete(reservation)
        session.commit()
        return {"message": "Reservation cancelled successfully"}

@app.get("/events/{event_id}/availability")
def get_event_availability(event_id: int):
    with Session(engine) as session:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        reservations = session.exec(select(Reservation).where(Reservation.event_id == event_id)).all()
        booked = len(reservations)
        remaining = event.capacity - booked
        return {
            "capacity": event.capacity,
            "booked": booked,
            "remaining": remaining
        }
