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
    @field_validator("academic_year")
    @classmethod
    def validate_academic_year(cls, v):
        try:
            start_year, end_year = map(int,v.split("-"))
        except:
            raise ValueError("Academic year must be in format YYYY-YYYY")
        if start_year >= end_year:
            raise ValueError("Academic year end must be greater than start year")
        if end_year - start_year != 1:
            raise ValueError("Academic year must span exactly one year")
        return v
class StudentCreate(BaseModel):
    student_name: str
    standard_id: int
    academic_year: str
    @field_validator("academic_year")
    @classmethod
    def validate_academic_year(cls, v):
        try:
            start_year, end_year = map(int,v.split("-"))
        except:
            raise ValueError("Academic year must be in format YYYY-YYYY")
        if start_year >= end_year:
            raise ValueError("Academic year end must be greater than start year")
        if end_year - start_year != 1:
            raise ValueError("Academic year must span exactly one year")
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
    academic_year: str