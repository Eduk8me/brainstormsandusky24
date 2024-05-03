SELECT 
s.PrimaryStudentID,
s.FirstName,
s.Lastname,
s.CourseName,
s.Term,
s.Period,
u.lastname AS 'Teacher'
FROM 
schedule s,users u
WHERE PrimaryStudentID='824068'
AND
s.TeacherID = u.teacher_code
