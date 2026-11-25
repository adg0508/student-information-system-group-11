-- 1. Which courses did each student take in fall 2026-2027?
SELECT s.student_no,
       s.first_name || ' ' || s.last_name AS student,
       c.code AS course, cs.section_no, e.grade
FROM sis.enrollment AS e
JOIN sis.student AS s ON s.student_id = e.student_id
JOIN sis.course_section AS cs ON cs.section_id = e.section_id
JOIN sis.course AS c ON c.course_id = cs.course_id
JOIN sis.semester AS sem ON sem.semester_id = cs.semester_id
WHERE sem.academic_year = '2026-2027' AND sem.term = 'Fall'
ORDER BY s.student_no, c.code;

-- 2. How many students took each course in fall 2026-2027, and what was their average grade?
SELECT c.code AS course, COUNT(DISTINCT e.student_id) AS students,
       ROUND(AVG(e.grade), 2) AS average_grade
FROM sis.course AS c
JOIN sis.course_section AS cs ON cs.course_id = c.course_id
JOIN sis.semester AS sem ON sem.semester_id = cs.semester_id
LEFT JOIN sis.enrollment AS e ON e.section_id = cs.section_id
WHERE sem.academic_year = '2026-2027' AND sem.term = 'Fall'
GROUP BY c.course_id, c.code
ORDER BY students DESC, c.code;

-- 3. Who scored above the class average in section 1 of CMPE341 in fall 2026-2027?
SELECT s.student_no,
       s.first_name || ' ' || s.last_name AS student, e.grade
FROM sis.student AS s
JOIN sis.enrollment AS e ON e.student_id = s.student_id
JOIN sis.course_section AS cs ON cs.section_id = e.section_id
JOIN sis.course AS c ON c.course_id = cs.course_id
JOIN sis.semester AS sem ON sem.semester_id = cs.semester_id
WHERE c.code = 'CMPE341' AND cs.section_no = 1
  AND sem.academic_year = '2026-2027' AND sem.term = 'Fall'
  AND e.grade > (
      SELECT AVG(other.grade)
      FROM sis.enrollment AS other
      WHERE other.section_id = e.section_id
  )
ORDER BY e.grade DESC, s.student_no;
