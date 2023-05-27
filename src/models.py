from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class Act(BaseModel):
    act_id: str
    title: str
    agency: str | None = None
    date_of_formation: date | None = None
    date_of_disbandment: date | None = None
    alternative_titles: list[str] | None = None


class Character(BaseModel):
    character_id: str
    title: str
    name: str
    act: str | None
    member_colors: list[str] | None = None
    date_joined: date | None = None
    date_left: date | None = None


class Person(BaseModel):
    person_id: str
    title: str
    name: str
    date_of_birth: date | None = None
    characters: list[Character]


class Venue(BaseModel):
    venue_id: str
    title: str
    latitude: str
    longitude: str
    full_address: str
    postal_code: str | None
    country: str | None
    subdivision: str | None
    municipality: str | None
    neighborhood: str | None


class Performance(BaseModel):
    start_time: datetime
    end_time: datetime
    participants: list[Act]


class Event(BaseModel):
    title: str
    date: list[date]
    venues: list[Venue]
    timetables: list[Performance]
    participants: list[str]


class Cost(BaseModel):
    price: float = 0.0
    currency: Literal["USD", "JPY", "EUR", "CND"] = "JPY"


class Cheki(BaseModel):
    format: Literal["mini", "wide", "square"]
    date: date | None
    event: Event | None
    venue: Venue | None
    subjects: list[Character]
    cost: Cost
    type: Literal["deco", "comment", "sign", "normal"]
    uri: str
