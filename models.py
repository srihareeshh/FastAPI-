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
class Standard(Base):
    __tablename__ = "standards"
    id = Column(Integer, primary_key=True, index=True)
    std_name = Column(String(50),nullable=False,unique=True)
    created_at = Column(DateTime,server_default=func.now(),nullable=False)
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now(),nullable=False)
    subjects = relationship("Subject",back_populates="standard")
    enrollments = relationship("StudentStandard",back_populates="standard")
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now(),nullable=False)
    is_active = Column(Boolean,default=True,nullable=False)
    enrollments = relationship("StudentStandard",back_populates="student")
class StudentStandard(Base):
    __tablename__ = "student_standards"
    __table_args__ = (UniqueConstraint("student_id","academic_year",name="unique_student_academic_year"),)
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer,ForeignKey("students.id"),nullable=False)
    standard_id = Column(Integer,ForeignKey("standards.id"),nullable=False)
    academic_year = Column(String(20),nullable=False)
    is_current = Column(Boolean,default=True,nullable=False)
    enrolled_at = Column(DateTime,server_default=func.now(),nullable=False)
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now(),nullable=False)
    student = relationship("Student",back_populates="enrollments")
    standard = relationship("Standard",back_populates="enrollments")
    marks = relationship("StudentMark",back_populates="student_standard")
class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), nullable=False)
    standard_id = Column(Integer,ForeignKey("standards.id"))
    standard = relationship("Standard", back_populates="subjects")
    marks = relationship("StudentMark",back_populates="subject")
    is_active = Column(Boolean,default=True,nullable=False)
    created_at = Column(DateTime,server_default=func.now(),nullable=False)
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now(),nullable=False)
    __table_args__ = (UniqueConstraint("standard_id","subject_name",name="unique_subject_per_standard"),)

class StudentMark(Base):
    __tablename__ = "student_marks"
    id = Column(Integer, primary_key=True, index=True)
    student_standard_id = Column(Integer,ForeignKey("student_standards.id"))
    subject_id = Column(Integer,ForeignKey("subjects.id"))
    marks = Column(Integer)
    created_at = Column(DateTime,server_default=func.now(),nullable=False)
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now(),nullable=False)
    student_standard = relationship("StudentStandard",back_populates="marks")
    subject = relationship("Subject",back_populates="marks")
    __table_args__ = (CheckConstraint("marks >= 0",name="check_marks_non_negative"),
    UniqueConstraint("student_standard_id","subject_id",name="unique_student_subject_mark"),)