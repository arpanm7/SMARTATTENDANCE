from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

DATABASE = "attendance.db"


def create_database():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            status TEXT NOT NULL,
            date TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO students (id, name) VALUES (?, ?)",
            [
                (1, "Student 1"),
                (2, "Student 2"),
                (3, "Student 3")
            ]
        )

    connection.commit()
    connection.close()


create_database()


class AttendanceRecord(BaseModel):
    student_id: int
    status: str


@app.get("/")
def home():
    return {"message": "Smart Attendance Backend is running!"}


@app.get("/students")
def get_students():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("SELECT id, name FROM students")
    rows = cursor.fetchall()

    connection.close()

    students = [
        {"id": row[0], "name": row[1]}
        for row in rows
    ]

    return {"students": students}


@app.post("/attendance")
def mark_attendance(record: AttendanceRecord):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO attendance (student_id, status) VALUES (?, ?)",
        (record.student_id, record.status)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Attendance recorded successfully",
        "student_id": record.student_id,
        "status": record.status
    }


@app.get("/attendance")
def get_attendance():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT attendance.id, students.name,
               attendance.status, attendance.date
        FROM attendance
        JOIN students
        ON attendance.student_id = students.id
    """)

    rows = cursor.fetchall()

    connection.close()

    records = [
        {
            "id": row[0],
            "student": row[1],
            "status": row[2],
            "date": row[3]
        }
        for row in rows
    ]

    return {"attendance": records}
