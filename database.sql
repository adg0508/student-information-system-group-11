-- CMPE341, Section 3, Group 11
-- Run once in a new PostgreSQL database.
BEGIN;
CREATE SCHEMA sis;

CREATE TABLE sis.department (
    department_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE sis.student (
    student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_no TEXT NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    department_id INTEGER NOT NULL REFERENCES sis.department(department_id)
);

CREATE TABLE sis.instructor (
    instructor_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    staff_no VARCHAR(10) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    department_id INTEGER NOT NULL REFERENCES sis.department(department_id)
);

CREATE TABLE sis.course (
    course_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    title VARCHAR(120) NOT NULL,
    credits INTEGER NOT NULL,
    department_id INTEGER NOT NULL REFERENCES sis.department(department_id)
);

CREATE TABLE sis.semester (
    semester_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    academic_year TEXT NOT NULL,
    term TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    UNIQUE (academic_year, term),
    CHECK (end_date > start_date)
);

CREATE TABLE sis.course_section (
    section_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES sis.course(course_id),
    instructor_id INTEGER NOT NULL REFERENCES sis.instructor(instructor_id),
    semester_id INTEGER NOT NULL REFERENCES sis.semester(semester_id),
    section_no INTEGER NOT NULL CHECK (section_no > 0),
    UNIQUE (course_id, semester_id, section_no)
);

CREATE TABLE sis.enrollment (
    enrollment_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES sis.student(student_id),
    section_id INTEGER NOT NULL REFERENCES sis.course_section(section_id),
    grade NUMERIC(5,2),
    UNIQUE (student_id, section_id)
);

INSERT INTO sis.department (code, name) VALUES
('CMPE', 'Computer Engineering'),
('SE', 'Software Engineering'),
('IE', 'Industrial Engineering');

INSERT INTO sis.student (student_no, first_name, last_name, email, department_id) VALUES
('23243510001', 'Ada', 'Yilmaz', 'ada.yilmaz@example.com', 1),
('23243510002', 'Eren', 'Kaya', 'eren.kaya@example.com', 1),
('23243610003', 'Selin', 'Demir', 'selin.demir@example.com', 2),
('23243710004', 'Mert', 'Arslan', 'mert.arslan@example.com', 3);

INSERT INTO sis.instructor (staff_no, first_name, last_name, email, department_id) VALUES
('I001', 'Deniz', 'Acar', 'deniz.acar@example.com', 1),
('I002', 'Elif', 'Yildiz', 'elif.yildiz@example.com', 2),
('I003', 'Can', 'Eren', 'can.eren@example.com', 3);

INSERT INTO sis.course (code, title, credits, department_id) VALUES
('CMPE341', 'Database Design and Management', 4, 1),
('SE301', 'Software Engineering', 4, 2),
('IE201', 'Operations Research', 3, 3);

INSERT INTO sis.semester (academic_year, term, start_date, end_date) VALUES
('2025-2026', 'Fall', '2025-09-22', '2026-01-09'),
('2025-2026', 'Spring', '2026-02-09', '2026-06-05'),
('2026-2027', 'Fall', '2026-09-21', '2027-01-08');

INSERT INTO sis.course_section (course_id, instructor_id, semester_id, section_no) VALUES
(1, 1, 3, 1), (2, 2, 3, 1), (3, 3, 3, 1), (1, 1, 2, 1);

INSERT INTO sis.enrollment (student_id, section_id, grade) VALUES
(1, 1, 90), (2, 1, 70), (3, 2, 85), (4, 3, 75),
(1, 4, 65), (2, 2, 80), (3, 1, NULL);
COMMIT;
