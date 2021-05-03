# CS554-Capstone1

How to create/access DB instance

```
from Bioada import DBHelper as db_con 
cursor = db_con.DBConnection.Instance().cursor
```

Comments: <br>
* L1 - Location of DBHelper file. <br>
* L2 - Remember: Do not directly invoke DBConnection's constructor.
