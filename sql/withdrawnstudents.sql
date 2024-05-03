select distinct `users`.`uid` AS `student_id`,
`users`.`firstname` AS `first_name`,
`users`.`lastname` AS `last_name`,
`users`.`username` AS `username`,
`users`.`status` AS `status` 
from `users` where (`users`.`uid` in (select `schedule`.`PrimaryStudentID` from `schedule`) is false and `users`.`uid` in 
    (select `users`.`uid` from `users` where ((`users`.`status` = 'Active') and (`users`.`type` = 'student'))))
