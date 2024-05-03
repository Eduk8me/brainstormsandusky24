-- Create a list of seniors in ELEA and HARB classrooms

SELECT DISTINCT users.uid,
                users.lastname,
                users.firstname,
                Coursename,
                TeacherID,
                Period,
                asset AS 'Assigned',
                '' AS 'Tub',
                '' AS 'Laptop ID#',
                '' AS 'Charger',
                '' AS 'Notes'
FROM
    users,schedule,chromebooks
WHERE
    users.uid = schedule.PrimaryStudentID
    AND users.uid = chromebooks.uid
    AND SiteID = 'High'
    AND (TeacherID = 'PORTECH' OR TeacherID = 'CONLEBR' OR TeacherID = 'STEWAEL')
    AND (Term = '4-9W' OR Term = 'Year'
    OR Term = '2SEM')
    AND schedule.Grade = '12'
    AND (CourseName LIKE '%ENG%' OR CourseName LIKE '%LIT%')
ORDER BY TeacherID, Period, Coursename, lastname , firstname
