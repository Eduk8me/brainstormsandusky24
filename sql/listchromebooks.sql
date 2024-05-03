SELECT users.uid,
    users.firstname,
    users.lastname,
    users.grade,
    chromebooks.asset,
    inventory.description
FROM users,chromebooks,inventory 
WHERE 
users.uid=chromebooks.uid 
AND 
chromebooks.asset=inventory.id
AND
grade="12"
ORDER BY users.lastname,users.firstname
