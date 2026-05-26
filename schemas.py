from datetime import datetime
from typing import Optional
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
    academic_year: str
class StudentCreate(BaseModel):
    student_name: str
    standard_id: int
    academic_year: str
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