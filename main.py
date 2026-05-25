from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Standard, Student, Subject, StudentMark
from schemas import (
    StandardCreate,
    StudentCreate,
    SubjectCreate,
    MarkCreate
)
Base.metadata.create_all(bind=engine)
app = FastAPI()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.post("/standards")
def create_standard(
    standard: StandardCreate,
    db: Session = Depends(get_db)
):
    db_standard = Standard(
        std_name=standard.std_name
    )
    db.add(db_standard)
    db.commit()
    db.refresh(db_standard)
    return db_standard
@app.post("/students")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    db_student = Student(
        student_name=student.student_name,
        standard_id=student.standard_id
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
@app.post("/subjects")
def create_subject(
    subject: SubjectCreate,
    db: Session = Depends(get_db)
):
    
        
    db_subject = Subject(
        subject_name=subject.subject_name,
        standard_id=subject.standard_id
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject
@app.post("/marks")
def add_marks(
    mark: MarkCreate,
    db: Session = Depends(get_db)

):
    db_mark = StudentMark(
        student_id=mark.student_id,
        subject_id=mark.subject_id,
        marks=mark.marks
    )
    db.add(db_mark)
    db.commit()
    db.refresh(db_mark)
    return db_mark