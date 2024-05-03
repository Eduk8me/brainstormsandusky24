-- Create a list of class lists based on 8th period
-- Do not include seniors in the list

SELECT DISTINCT users.uid,
                users.lastname,
                users.firstname,
                Coursename,
                TeacherID,
                Period,
                asset AS 'Assigned',
                '' AS 'Laptop ID#',
                '' AS 'Charger'
FROM
    users,schedule,chromebooks
WHERE
    users.uid = schedule.PrimaryStudentID
    AND users.uid = chromebooks.uid
    AND SiteID = 'High'
    AND Period = '08'
    AND Grade != '12'
    AND (Term = '4-9W' OR Term = 'Year'
    OR Term = '2SEM')
ORDER BY TeacherID, Period, Coursename, lastname , firstname

