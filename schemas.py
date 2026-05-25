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
class StudentCreate(BaseModel):
    student_name: str
    standard_id: int
    created_at:datetime
class SubjectCreate(BaseModel):
    subject_name: str
    standard_id: int
    
class MarkCreate(BaseModel):
    student_id: int
    subject_id: int
    marks: int
    created_at:datetime
    updated_at:datetime