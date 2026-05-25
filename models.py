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
    subjects = relationship("Subject",back_populates="standard")
    enrollments = relationship("StudentStandard",back_populates="standard")
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    marks = relationship("StudentMark",back_populates="student")
    enrollments = relationship("StudentStandard",back_populates="student")
class StudentStandard(Base):
    __tablename__ = "student_standards"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer,ForeignKey("students.id"),nullable=False)
    standard_id = Column(Integer,ForeignKey("standards.id"),nullable=False)
    is_current = Column(Boolean,default=True,nullable=False)
    enrolled_at = Column(DateTime,server_default=func.now(),nullable=False)
    student = relationship("Student",back_populates="enrollments")
    standard = relationship("Standard",back_populates="enrollments")
class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), nullable=False)
    standard_id = Column(Integer,ForeignKey("standards.id"))
    standard = relationship("Standard", back_populates="subjects")
    marks = relationship("StudentMark",back_populates="subject")

class StudentMark(Base):
    __tablename__ = "student_marks"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer,ForeignKey("students.id"))
    subject_id = Column(Integer,ForeignKey("subjects.id"))
    marks = Column(Integer)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    student = relationship("Student", back_populates="marks")
    subject = relationship("Subject", back_populates="marks")