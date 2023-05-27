from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class Performers(BaseModel):
    title: str
    agency: str | None = None
    date_of_formation: date
    date_of_disbandment: date | None = None
    alternative_titles: list[str] | None = None


class Person(BaseModel):
    name: str
    date_of_birth: date


class Character(BaseModel):
    name: str
    group: Performers | None
    person: Person
    member_color: str | None = None
    date_joined: date
    date_left: date


class Location(BaseModel):
    lat: str
    lon: str
    address: str
    country: str
    subdivision_1: str | None
    subdivision_2: str | None
    municipality: str | None
    postal_code: str


class Venue(BaseModel):
    title: str
    location: Location


class Performance(BaseModel):
    start_time: datetime
    end_time: datetime
    participants: list[Performers]


class Event(BaseModel):
    title: str
    date: list[date]
    venues: list[Venue]
    timetables: list[Performance]
    participants: list[str]


class Cheki(BaseModel):
    format: Literal["mini", "wide", "square"]
    date: date
    event: Event | None
    venue: Venue | None
    subjects: list[Character]
    cost: float
    type: Literal["deco", "comment", "sign", "normal"]
    uri: str
