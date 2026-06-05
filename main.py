from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi import UploadFile, File
import cloudinary.uploader
from passlib.context import CryptContext
from jose import jwt
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from models import User
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
    SubjectUpdate,
    ReactivateStudent,
    UserCreate
)
import cloudinary
cloudinary.config(
    cloud_name="",
    api_key="",
    api_secret="****"
)
Base.metadata.create_all(bind=engine)
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_or_404(model,obj_id: int,db: Session,entity_name: str):
    obj = db.query(model).filter(model.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404,detail=f"{entity_name} not found")
    return obj
def get_student(student_id: int,db: Session):
    return get_or_404(Student,student_id,db,"Student")
def get_standard(standard_id: int,db: Session):
    return get_or_404(Standard,standard_id,db,"Standard")
def get_subject(subject_id: int,db: Session):
    return get_or_404(Subject,subject_id,db,"Subject")
def get_enrollment(enrollment_id: int,db: Session):
    return get_or_404(StudentStandard,enrollment_id,db,"Enrollment")
def get_mark(mark_id: int,db: Session):
    return get_or_404(StudentMark,mark_id,db,"Mark")
def build_academic_year(
    start_year: int
):
    return (
        f"{start_year}-"
        f"{start_year + 1}"
    )
def hash_password(password: str):
    return pwd_context.hash(password)
def verify_password(plain_password: str,hashed_password: str):
    return pwd_context.verify(plain_password,hashed_password)
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update(
        {
            "exp": expire
        }
    )
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401,detail="Invalid token")
        return {
            "username": username,
            "role": role
        }
    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid token")
@app.post("/standards",tags=["Standards"],summary="Create a standard")
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
@app.post("/students",tags=["Students"],summary="Create a new student")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    get_standard(student.standard_id,db)
    db_student = Student(student_name=student.student_name,is_active=True)
    db.add(db_student)
    db.flush()
    enrollment = StudentStandard(student_id=db_student.id,standard_id=student.standard_id,academic_year=build_academic_year(student.start_year),is_current=True)
    db.add(enrollment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="Student already has enrollment for this academic year")
    db.refresh(db_student)
    return db_student
@app.post("/enrollments",tags=["Enrollments"],summary="Enroll a student")
def enroll_student(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db)
):
    student = get_student(enrollment.student_id,db)
    if student.is_active == False:
        raise HTTPException(
            status_code=400,
            detail="Cannot enroll inactive student"
        )
    get_standard(enrollment.standard_id,db)
    new_academic_year = build_academic_year(enrollment.start_year)
    existing_year_enrollment = db.query(StudentStandard).filter(
    StudentStandard.student_id == enrollment.student_id,
    StudentStandard.academic_year == new_academic_year).first()
    if existing_year_enrollment:
        raise HTTPException(status_code=409,detail="Student already has enrollment for this academic year")
    latest_enrollment = db.query(StudentStandard).filter(StudentStandard.student_id == enrollment.student_id).order_by(StudentStandard.academic_year.desc()).first()
    if latest_enrollment:
        latest_start_year = int(latest_enrollment.academic_year.split("-")[0])
        if enrollment.start_year <= latest_start_year:
            raise HTTPException(status_code=400,detail="Academic year must be greater than previous enrollment year")
    current_enrollments = db.query(StudentStandard).filter(
        StudentStandard.student_id == enrollment.student_id,
        StudentStandard.is_current == True
    ).all()
    for row in current_enrollments:
        row.is_current = False
    new_enrollment = StudentStandard(
        student_id=enrollment.student_id,
        standard_id=enrollment.standard_id,
        academic_year=build_academic_year(enrollment.start_year),
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
@app.post("/subjects",tags=["Subjects"],summary="Create a subject")
def create_subject(
    subject: SubjectCreate,
    db: Session = Depends(get_db)
):
    get_standard(subject.standard_id,db)
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
            status_code=409,detail="Subject already exists for this standard")
    db.refresh(db_subject)
    return db_subject
@app.post("/marks",tags=["Marks"],summary="Add marks")
def add_marks(
    mark: MarkCreate,
    db: Session = Depends(get_db)
):
    enrollment = get_enrollment(mark.student_standard_id,db)
    subject = get_subject(mark.subject_id,db)
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
@app.get("/standards",tags=["Standards"],summary="Get all standards")
def get_standards(
    db: Session = Depends(get_db)
):
    standards = db.query(Standard).all()
    return standards
@app.get("/students",tags=["Students"],summary="Get all active students")
def get_students(
    db: Session = Depends(get_db)
):
    students = db.query(Student).filter(Student.is_active == True).all()
    return students
@app.get("/subjects",tags=["Subjects"],summary="Get all active subjects")
def get_subjects(
    db: Session = Depends(get_db)
):
    subjects = db.query(Subject).filter(Subject.is_active == True).all()
    return subjects
@app.get("/enrollments",tags=["Enrollments"],summary="Get all enrollments")
def get_enrollments(
    db: Session = Depends(get_db)
):
    enrollments = db.query(StudentStandard).all()
    return enrollments
@app.get("/marks",tags=["Marks"],summary="Get all marks")
def get_marks(
    db: Session = Depends(get_db)
):
    marks = db.query(StudentMark).all()
    return marks
@app.get("/students/{student_id}",tags=["Students"],summary="Get student by ID")
def get_student_by_id(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = get_student(student_id,db)
    if not student.is_active:
        raise HTTPException(status_code=404,detail="Student not found")
    return student
@app.get("/standards/{standard_id}",tags=["Standards"],summary="Get standard by ID")
def get_standard_by_id(
    standard_id: int,
    db: Session = Depends(get_db)
):
    return get_standard(standard_id,db)
@app.get("/subjects/{subject_id}",tags=["Subjects"],summary="Get subject by ID")
def get_subject_by_id(
    subject_id: int,
    db: Session = Depends(get_db)
):
    subject=get_subject(subject_id,db)
    if not subject.is_active:
        raise HTTPException(status_code=404,detail="Subject not found")
    return subject
@app.get("/enrollments/{enrollment_id}",tags=["Enrollments"],summary="Get enrollment by ID")
def get_enrollment_by_id(
    enrollment_id: int,
    db: Session = Depends(get_db)
):
    return get_enrollment(enrollment_id,db)
@app.get("/marks/{mark_id}",tags=["Marks"],summary="Get mark by ID")
def get_mark_by_id(
    mark_id: int,
    db: Session = Depends(get_db)
):
    return get_mark(mark_id,db)
@app.put("/marks/{mark_id}",tags=["Marks"],summary="Update marks")
def update_mark(
    mark_id: int,
    updated_mark: MarkUpdate,
    db: Session = Depends(get_db)
):
    db_mark = get_mark(mark_id,db)
    db_mark.marks = updated_mark.marks
    db.commit()
    db.refresh(db_mark)
    return db_mark
@app.delete("/marks/{mark_id}",tags=["Marks"],summary="Delete marks")
def delete_mark(
    mark_id: int,
    db: Session = Depends(get_db)
):
    db_mark = get_mark(mark_id,db)
    db.delete(db_mark)
    db.commit()
    return {
        "message": "Mark deleted successfully"
    }
@app.put("/students/{student_id}",tags=["Students"])
def update_student(
    student_id: int,
    updated_student: StudentUpdate,
    db: Session = Depends(get_db)
):
    db_student = get_student(student_id,db)
    if db_student.is_active == False:
        raise HTTPException(status_code=400,detail="Cannot update inactive student")
    db_student.student_name = updated_student.student_name
    db.commit()
    db.refresh(db_student)
    return db_student
@app.put("/subjects/{subject_id}",tags=["Subjects"],summary="Update a subject")
def update_subject(
    subject_id: int,
    updated_subject: SubjectUpdate,
    db: Session = Depends(get_db)
):
    db_subject = get_subject(subject_id,db)
    if db_subject.is_active == False:
        raise HTTPException(status_code=400,detail="Cannot update inactive subject")
    db_subject.subject_name = updated_subject.subject_name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="Subject already exists for this standard")
    db.refresh(db_subject)
    return db_subject
@app.delete("/subjects/{subject_id}",tags=["Subjects"],summary="Deactivate a subject")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db)
):
    db_subject = get_subject(subject_id,db)
    db_subject.is_active = False
    db.commit()
    db.refresh(db_subject)
    return {
        "message": "Subject deactivated successfully"
    }
@app.delete("/students/{student_id}",tags=["Students"])
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    db_student = get_student(student_id,db)
    current_enrollments = db.query(StudentStandard).filter(
        StudentStandard.student_id == student_id,
        StudentStandard.is_current == True
    ).all()

    for row in current_enrollments:
        row.is_current = False
    db_student.is_active = False
    db.commit()
    db.refresh(db_student)
    return {
        "message": "Student deactivated successfully"
    }
@app.put("/students/reactivate/{student_id}",tags=["Students"])
def reactivate_student(
    student_id: int,
    enrollment: ReactivateStudent,
    db: Session = Depends(get_db)
):
    existing_student = get_student(student_id,db)
    if existing_student.is_active == True:
        raise HTTPException(status_code=400,detail="Student is already active")
    get_standard(enrollment.standard_id,db)
    latest_enrollment = db.query(StudentStandard).filter(
        StudentStandard.student_id == student_id
    ).order_by(
        StudentStandard.academic_year.desc()
    ).first()
    if latest_enrollment:
        latest_start_year = int(latest_enrollment.academic_year.split("-")[0])
        new_start_year = enrollment.start_year
        if new_start_year <= latest_start_year:
            raise HTTPException(status_code=400,detail="Academic year must be greater than previous enrollment year")
        if enrollment.standard_id < latest_enrollment.standard_id:
            raise HTTPException(status_code=400,detail="Student cannot be enrolled in a lower standard")
    current_enrollments = db.query(StudentStandard).filter(
        StudentStandard.student_id == student_id,
        StudentStandard.is_current == True
    ).all()
    for row in current_enrollments:
        row.is_current = False
    existing_student.is_active = True
    new_enrollment = StudentStandard(
        student_id=student_id,
        standard_id=enrollment.standard_id,
        academic_year=build_academic_year(enrollment.start_year),
        is_current=True
    )
    db.add(new_enrollment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="Student already has enrollment for this academic year")
    db.refresh(existing_student)
    return {
        "message": "Student reactivated successfully"
    }
@app.get("/students/{student_id}/report",tags=["Students"],summary="Get student by ID")
def get_student_report(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = get_student(student_id, db)
    current_enrollment = db.query(StudentStandard).filter(
        StudentStandard.student_id == student_id,
        StudentStandard.is_current == True
    ).first()
    if not current_enrollment:
        raise HTTPException(status_code=404,detail="No active enrollment found")
    standard = get_standard(current_enrollment.standard_id,db)
    marks = db.query(StudentMark).filter(StudentMark.student_standard_id == current_enrollment.id).all()
    subject_report = []
    total = 0
    for mark in marks:
        subject = get_subject(mark.subject_id,db)
        subject_report.append(
            {
                "subject": subject.subject_name,
                "marks": mark.marks
            }
        )
        total += mark.marks
    average = 0
    if len(marks) > 0:
        average = total / len(marks)
    return {
        "student_id": student.id,
        "student_name": student.student_name,
        "standard": standard.std_name,
        "academic_year": current_enrollment.academic_year,
        "subjects": subject_report,
        "total": total,
        "average": average
    }
@app.post("/students/{student_id}/profile-image",tags=["Students"])
def upload_student_image(student_id: int,image: UploadFile = File(...),db: Session = Depends(get_db)):
    student = get_student(student_id,db)
    allowed_types = [
    "image/jpeg",
    "image/png",
    "image/webp"
]
    if image.content_type not in allowed_types:
        raise HTTPException(status_code=400,detail="Only JPG, PNG and WEBP images are allowed")
    try:
        upload_result = cloudinary.uploader.upload(
            image.file,
            folder=f"students/{student_id}"
        )
    except Exception:
        raise HTTPException(status_code=500,detail="Failed to upload image")
    student.profile_image = (upload_result["secure_url"])
    try:
        db.commit()
        db.refresh(student)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500,detail="Failed to save image URL")
    return {"message": "Image uploaded successfully","image_url": student.profile_image}
@app.post("/users",tags=["Users"],summary="Create a user")
def create_user(user: UserCreate,db: Session = Depends(get_db)):
    db_user = User(username=user.username,password_hash=hash_password(user.password),role=user.role)
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="Username already exists")
    db.refresh(db_user)
    return {
        "message": "User created successfully"
    }
@app.post("/login",tags=["Authentication"],summary="Login user")
def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()
    if not user:
        raise HTTPException(status_code=401,detail="Invalid username or password")
    if not verify_password(form_data.password,user.password_hash):
        raise HTTPException(status_code=401,detail="Invalid username or password")
    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role
        }
    )
    return {
        "access_token": token,
        "token_type": "bearer"
    }
@app.get("/me",tags=["Authentication"])
def get_me(
    current_user = Depends(get_current_user)
):
    return current_user