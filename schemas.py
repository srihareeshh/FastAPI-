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
class StudentCreate(BaseModel):
    student_name: str
    standard_id: int
class SubjectCreate(BaseModel):
    subject_name: str
    standard_id: int
class MarkCreate(BaseModel):
    student_standard_id: int
    subject_id: int
    marks: int
    