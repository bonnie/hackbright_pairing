SELECT CONCAT(CASE WHEN nickname != '' THEN nickname ELSE first_name END, ' ', last_name) AS name, sis_studentlevel.level
FROM sis_student
JOIN sis_studentlevel ON sis_student.id = sis_studentlevel.student_id
JOIN sis_cohorthouse ON sis_student.house_id = sis_cohorthouse.id
WHERE sis_student.cohort_id='f18k'
   AND sis_student.status = 'published'
   AND sis_studentlevel.created IN
    (SELECT MAX(sis_studentlevel.created)
     FROM sis_studentlevel
     JOIN sis_student ON sis_student.id = sis_studentlevel.student_id
     GROUP BY sis_student.id) 
GROUP BY sis_cohorthouse.title,
         sis_student.id,
         sis_studentlevel.level,
         sis_studentlevel.created
ORDER BY sis_studentlevel.level;