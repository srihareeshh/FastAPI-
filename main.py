from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import (
    Base,
    Standard,
    Student,
    StudentStandard,
    Subject,
    StudentMark
)

from schemas import (
    StandardCreate,
    StudentCreate,
    EnrollmentCreate,
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
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Standard already exists"
        )
    db.refresh(db_standard)
    return db_standard
@app.post("/students")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    db_student = Student(
        student_name=student.student_name
    )
    db.add(db_student)
    db.flush()
    enrollment = StudentStandard(
    student_id=db_student.id,
    standard_id=student.standard_id,
    academic_year=student.academic_year,
    is_current=True
    )
    db.add(enrollment)
    db.commit()
    db.refresh(db_student)
    return db_student
@app.post("/enrollments")
def enroll_student(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == enrollment.student_id).first()
    if not student:
        raise HTTPException(status_code=404,detail="Student not found")
    standard = db.query(Standard).filter(Standard.id == enrollment.standard_id).first()
    if not standard:
        raise HTTPException(status_code=404,detail="Standard not found")
    existing_current = db.query(StudentStandard).filter(
    StudentStandard.student_id == enrollment.student_id,
    StudentStandard.standard_id == enrollment.standard_id,
    StudentStandard.academic_year == enrollment.academic_year
).first()
    if existing_current:
        raise HTTPException (status_code=409,detail="Student already existing in this standard")

    current_enrollments = db.query(StudentStandard).filter(StudentStandard.student_id == enrollment.student_id,StudentStandard.is_current == True).all()
    for row in current_enrollments:
        row.is_current = False
    new_enrollment = StudentStandard(
    student_id=enrollment.student_id,
    standard_id=enrollment.standard_id,
    academic_year=enrollment.academic_year,
    is_current=True
    )
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return {
    "message": "Student enrolled successfully",
    "enrollment_id": new_enrollment.id,
    "student_id": new_enrollment.student_id,
    "standard_id": new_enrollment.standard_id,
    "academic_year": new_enrollment.academic_year,
    "is_current": new_enrollment.is_current
}
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
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Subject already exists for this standard"
        )
    db.refresh(db_subject)
    return db_subject
@app.post("/marks")
def add_marks(
    mark: MarkCreate,
    db: Session = Depends(get_db)
):
    enrollment = db.query(StudentStandard).filter(
        StudentStandard.id == mark.student_standard_id).first()
    if not enrollment:
        raise HTTPException(status_code=404,detail="Enrollment not found")
    subject = db.query(Subject).filter(Subject.id == mark.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404,detail="Subject not found")
    if enrollment.standard_id != subject.standard_id:
        raise HTTPException(status_code=400,detail="Subject does not belong to student's standard")
    db_mark = StudentMark(
        student_standard_id=mark.student_standard_id,
        subject_id=mark.subject_id,
        marks=mark.marks
    )
    db.add(db_mark)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Marks already entered for this subject"
        )
    db.refresh(db_mark)
    return db_mark