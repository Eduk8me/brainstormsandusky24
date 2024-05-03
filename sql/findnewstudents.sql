select distinct `schedule`.`PrimaryStudentID` AS `PrimaryStudentID`,
`schedule`.`Grade` AS `Grade`,
`schedule`.`FirstName` AS `FirstName`,
`schedule`.`Lastname` AS `Lastname`,
`schedule`.`SiteID` AS `SiteID` 
from `schedule` where 
(`schedule`.`PrimaryStudentID` in (select `users`.`uid` from `users`) is false or 
    `schedule`.`PrimaryStudentID` in (select `users`.`uid` from `users` where (`users`.`status` = 'inactive')));
