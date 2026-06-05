from datetime import datetime
from typing import Optional
from typing import Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)
class StandardCreate(BaseModel):
    std_name: str
class EnrollmentCreate(BaseModel):
    student_id: int
    standard_id: int
    start_year: int
    @field_validator("start_year")
    @classmethod
    def validate_start_year(cls, v):

        if v < 2000:
            raise ValueError(
                "Academic year must be 2000 or later"
            )

        return v
class StudentCreate(BaseModel):
    student_name: str
    standard_id: int
    start_year: int
    @field_validator("start_year")
    @classmethod
    def validate_start_year(cls, v):

        if v < 2000:
            raise ValueError(
                "Academic year must be 2000 or later"
            )

        return v
class SubjectCreate(BaseModel):
    subject_name: str
    standard_id: int
class MarkCreate(BaseModel):
    student_standard_id: int
    subject_id: int
    marks: int
    @field_validator("marks")
    @classmethod
    def validate_marks(cls, value):
        if value < 0:
            raise ValueError(
                "Marks cannot be negative"
            )
        return value
class MarkUpdate(BaseModel):
    marks: int
    @field_validator("marks")
    @classmethod
    def marks_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Marks cannot be negative")
        return v
class StudentUpdate(BaseModel):
    student_name: str
class SubjectUpdate(BaseModel):
    subject_name: str
class ReactivateStudent(BaseModel):
    standard_id: int
    start_year: str
class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["Admin","Teacher","Student"]