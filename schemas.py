from pydantic import BaseModel
class StandardCreate(BaseModel):
    std_name: str
class StudentCreate(BaseModel):
    student_name: str
    standard_id: int
class SubjectCreate(BaseModel):
    subject_name: str
    standard_id: int
class MarkCreate(BaseModel):
    student_id: int
    subject_id: int
    marks: int