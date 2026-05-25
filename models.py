from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
class Standard(Base):
    __tablename__ = "standards"
    id = Column(Integer, primary_key=True, index=True)
    std_name = Column(String(50), nullable=False)
    students = relationship("Student", back_populates="standard")
    subjects = relationship("Subject", back_populates="standard")
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=False)
    standard_id = Column(
        Integer,
        ForeignKey("standards.id")
    )
    standard = relationship("Standard", back_populates="students")
    marks = relationship(
        "StudentMark",
        back_populates="student"
    )
class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), nullable=False)
    standard_id = Column(
        Integer,
        ForeignKey("standards.id")
    )
    standard = relationship("Standard", back_populates="subjects")
    marks = relationship(
        "StudentMark",
        back_populates="subject"
    )
class StudentMark(Base):
    __tablename__ = "student_marks"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        Integer,
        ForeignKey("students.id")
    )
    subject_id = Column(
        Integer,
        ForeignKey("subjects.id")
    )
    marks = Column(Integer)
    student = relationship("Student", back_populates="marks")
    subject = relationship("Subject", back_populates="marks")