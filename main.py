from fastapi import FastAPI, Depends, HTTPException
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
    MarkCreate,
    MarkUpdate,
    StudentUpdate,
    SubjectUpdate
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
    standard = db.query(Standard).filter(Standard.id == student.standard_id).first()
    if not standard:
        raise HTTPException(status_code=404,detail="Standard not found")
    if student.student_id:

        existing_student = db.query(Student).filter(
            Student.id == student.student_id
        ).first()

        if not existing_student:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )
        if existing_student.student_name != student.student_name:
            raise HTTPException(
                status_code=400,
                detail="Student name does not match student ID"
            )

        if existing_student.is_active == True:
            raise HTTPException(
                status_code=400,
                detail="Student is already active"
            )

        latest_enrollment = db.query(StudentStandard).filter(
            StudentStandard.student_id == student.student_id
        ).order_by(
            StudentStandard.academic_year.desc()
        ).first()

        if latest_enrollment:

            latest_start_year = int(
                latest_enrollment.academic_year.split("-")[0]
            )

            new_start_year = int(
                student.academic_year.split("-")[0]
            )

            if new_start_year <= latest_start_year:

                raise HTTPException(
                    status_code=400,
                    detail="Academic year must be greater than previous enrollment year"
                )

        current_enrollments = db.query(StudentStandard).filter(
            StudentStandard.student_id == student.student_id,
            StudentStandard.is_current == True
        ).all()

        for row in current_enrollments:
            row.is_current = False

        existing_student.is_active = True

        enrollment = StudentStandard(
            student_id=existing_student.id,
            standard_id=student.standard_id,
            academic_year=student.academic_year,
            is_current=True
        )

        db.add(enrollment)

        try:
            db.commit()

        except IntegrityError:

            db.rollback()

            raise HTTPException(
                status_code=409,
                detail="Student already has enrollment for this academic year"
            )

        db.refresh(existing_student)

        return {
            "message": "Inactive student reactivated successfully"
        }
    db_student = Student(student_name=student.student_name,is_active=True)
    db.add(db_student)
    db.flush()
    enrollment = StudentStandard(student_id=db_student.id,standard_id=student.standard_id,academic_year=student.academic_year,is_current=True)
    db.add(enrollment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="Student already has enrollment for this academic year")
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
    if student.is_active == False:
        raise HTTPException(
            status_code=400,
            detail="Cannot enroll inactive student"
        )
    standard = db.query(Standard).filter(Standard.id == enrollment.standard_id).first()
    if not standard:
        raise HTTPException(status_code=404,detail="Standard not found")
    existing_year_enrollment = db.query(StudentStandard).filter(
        StudentStandard.student_id == enrollment.student_id,
        StudentStandard.academic_year == enrollment.academic_year
    ).first()
    if existing_year_enrollment:
        raise HTTPException(status_code=409,detail="Student already has enrollment for this academic year")
    latest_enrollment = db.query(StudentStandard).filter(StudentStandard.student_id == enrollment.student_id).order_by(StudentStandard.academic_year.desc()).first()
    if latest_enrollment:
        latest_start_year = int(
            latest_enrollment.academic_year.split("-")[0]
        )
        new_start_year = int(
            enrollment.academic_year.split("-")[0]
        )
        if new_start_year <= latest_start_year:
            raise HTTPException(
                status_code=400,
                detail="Academic year must be greater than previous enrollment year"
            )
    current_enrollments = db.query(StudentStandard).filter(
        StudentStandard.student_id == enrollment.student_id,
        StudentStandard.is_current == True
    ).all()
    for row in current_enrollments:
        row.is_current = False
    new_enrollment = StudentStandard(
        student_id=enrollment.student_id,
        standard_id=enrollment.standard_id,
        academic_year=enrollment.academic_year,
        is_current=True
    )
    db.add(new_enrollment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="Student already has enrollment for this academic year")
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
    standard = db.query(Standard).filter(
        Standard.id == subject.standard_id
    ).first()
    if not standard:
        raise HTTPException(
            status_code=404,
            detail="Standard not found"
        )
    existing_subject = db.query(Subject).filter(
    Subject.subject_name == subject.subject_name,
    Subject.standard_id == subject.standard_id,
    Subject.is_active == False
).first()
    if existing_subject:
        existing_subject.is_active = True
        db.commit()
        db.refresh(existing_subject)
        return {
            "message": "Inactive subject reactivated successfully"
        }
    db_subject = Subject(subject_name=subject.subject_name,standard_id=subject.standard_id)
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
        StudentStandard.id == mark.student_standard_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404,detail="Enrollment not found")
    subject = db.query(Subject).filter(
    Subject.id == mark.subject_id,
    Subject.is_active == True
).first()
    if not subject:
        raise HTTPException(status_code=404,detail="Subject not found")
    if enrollment.standard_id != subject.standard_id:
        raise HTTPException(status_code=400,detail="Subject does not belong to student's standard")
    db_mark = StudentMark(student_standard_id=mark.student_standard_id,subject_id=mark.subject_id,marks=mark.marks)
    db.add(db_mark)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="Marks already entered for this subject" )
    db.refresh(db_mark)
    return db_mark
@app.get("/standards")
def get_standards(
    db: Session = Depends(get_db)
):
    standards = db.query(Standard).all()
    return standards
@app.get("/students")
def get_students(
    db: Session = Depends(get_db)
):
    students = db.query(Student).filter(Student.is_active == True).all()
    return students
@app.get("/subjects")
def get_subjects(
    db: Session = Depends(get_db)
):
    subjects = db.query(Subject).filter(Subject.is_active == True).all()
    return subjects
@app.get("/enrollments")
def get_enrollments(
    db: Session = Depends(get_db)
):
    enrollments = db.query(StudentStandard).all()
    return enrollments
@app.get("/marks")
def get_marks(
    db: Session = Depends(get_db)
):
    marks = db.query(StudentMark).all()
    return marks
@app.get("/students/{student_id}")
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
    Student.id == student_id,
    Student.is_active == True
).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    return student
@app.get("/standards/{standard_id}")
def get_standard(
    standard_id: int,
    db: Session = Depends(get_db)
):
    standard = db.query(Standard).filter(
        Standard.id == standard_id
    ).first()
    if not standard:
        raise HTTPException(
            status_code=404,
            detail="Standard not found"
        )
    return standard
@app.get("/subjects/{subject_id}")
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(
    Subject.id == subject_id,
    Subject.is_active == True
).first()
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )
    return subject
@app.get("/enrollments/{enrollment_id}")
def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db)
):
    enrollment = db.query(StudentStandard).filter(
        StudentStandard.id == enrollment_id
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Enrollment not found"
        )
    return enrollment
@app.get("/marks/{mark_id}")
def get_mark(
    mark_id: int,
    db: Session = Depends(get_db)
):
    mark = db.query(StudentMark).filter(
        StudentMark.id == mark_id
    ).first()
    if not mark:
        raise HTTPException(
            status_code=404,
            detail="Mark not found"
        )
    return mark
@app.put("/marks/{mark_id}")
def update_mark(
    mark_id: int,
    updated_mark: MarkUpdate,
    db: Session = Depends(get_db)
):
    db_mark = db.query(StudentMark).filter(
        StudentMark.id == mark_id
    ).first()
    if not db_mark:
        raise HTTPException(
            status_code=404,
            detail="Mark not found"
        )
    db_mark.marks = updated_mark.marks
    db.commit()
    db.refresh(db_mark)
    return db_mark
@app.delete("/marks/{mark_id}")
def delete_mark(
    mark_id: int,
    db: Session = Depends(get_db)
):
    db_mark = db.query(StudentMark).filter(
        StudentMark.id == mark_id
    ).first()
    if not db_mark:
        raise HTTPException(status_code=404,detail="Mark not found")
    db.delete(db_mark)
    db.commit()
    return {
        "message": "Mark deleted successfully"
    }
@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    updated_student: StudentUpdate,
    db: Session = Depends(get_db)
):
    db_student = db.query(Student).filter(
        Student.id == student_id
    ).first()
    if not db_student:
        raise HTTPException(status_code=404,detail="Student not found")
    db_student.student_name = updated_student.student_name
    db.commit()
    db.refresh(db_student)
    return db_student
@app.put("/subjects/{subject_id}")
def update_subject(
    subject_id: int,
    updated_subject: SubjectUpdate,
    db: Session = Depends(get_db)
):
    db_subject = db.query(Subject).filter(
        Subject.id == subject_id
    ).first()
    if not db_subject:
        raise HTTPException(status_code=404,detail="Subject not found")
    db_subject.subject_name = updated_subject.subject_name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="Subject already exists for this standard")
    db.refresh(db_subject)
    return db_subject
@app.delete("/subjects/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db)
):
    db_subject = db.query(Subject).filter(
        Subject.id == subject_id
    ).first()
    if not db_subject:
        raise HTTPException(status_code=404,detail="Subject not found")
    db_subject.is_active = False
    db.commit()
    db.refresh(db_subject)
    return {
        "message": "Subject deactivated successfully"
    }
@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    db_student = db.query(Student).filter(
        Student.id == student_id
    ).first()
    if not db_student:
        raise HTTPException(status_code=404,detail="Student not found")
    db_student.is_active = False
    db.commit()
    db.refresh(db_student)
    return {
        "message": "Student deactivated successfully"
    }