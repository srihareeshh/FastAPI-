from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
class TimestampMixin:
    created_at = Column(DateTime,server_default=func.now(),nullable=False)
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now(),nullable=False)
class Standard(Base, TimestampMixin):
    __tablename__ = "standards"
    id = Column(Integer, primary_key=True, index=True)
    std_name = Column(String(50),nullable=False,unique=True)
    subjects = relationship("Subject",back_populates="standard")
    enrollments = relationship("StudentStandard",back_populates="standard")
class Student(Base, TimestampMixin):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=False)
    is_active = Column(Boolean,default=True,nullable=False)
    enrollments = relationship("StudentStandard",back_populates="student")
    profile_image = Column(String(500),nullable=True)
class StudentStandard(Base, TimestampMixin):
    __tablename__ = "student_standards"
    __table_args__ = (UniqueConstraint("student_id","academic_year",name="unique_student_academic_year"),)
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer,ForeignKey("students.id"),nullable=False)
    standard_id = Column(Integer,ForeignKey("standards.id"),nullable=False)
    academic_year = Column(Integer,nullable=False)
    is_current = Column(Boolean,default=True,nullable=False)
    enrolled_at = Column(DateTime,server_default=func.now(),nullable=False)
    student = relationship("Student",back_populates="enrollments")
    standard = relationship("Standard",back_populates="enrollments")
    marks = relationship("StudentMark",back_populates="student_standard")
class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), nullable=False)
    standard_id = Column(Integer,ForeignKey("standards.id"))
    standard = relationship("Standard", back_populates="subjects")
    marks = relationship("StudentMark",back_populates="subject")
    is_active = Column(Boolean,default=True,nullable=False)
    __table_args__ = (UniqueConstraint("standard_id","subject_name",name="unique_subject_per_standard"),)
class StudentMark(Base, TimestampMixin):
    __tablename__ = "student_marks"
    id = Column(Integer, primary_key=True, index=True)
    student_standard_id = Column(Integer,ForeignKey("student_standards.id"))
    subject_id = Column(Integer,ForeignKey("subjects.id"))
    marks = Column(Integer)
    student_standard = relationship("StudentStandard",back_populates="marks")
    subject = relationship("Subject",back_populates="marks")
    __table_args__ = (CheckConstraint("marks >= 0",name="check_marks_non_negative"),
    UniqueConstraint("student_standard_id","subject_id",name="unique_student_subject_mark"),)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String(100),unique=True,nullable=False)
    password_hash = Column(String(255),nullable=False)
    role = Column(String(20),nullable=False)
    student_id = Column(Integer,ForeignKey("students.id"),nullable=True)
    last_login = Column(DateTime,nullable=True)
    is_active = Column(Boolean,default=True)