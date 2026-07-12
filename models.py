import config 
import mysql.connector 
from mysql.connector import errorcode
from datetime import datetime ,date
from werkzeug.security import generate_password_hash , check_password_hash
DB_name=config.DB_name

cnx = None
cursor =None

# cnx = mysql.connector.connect(user='root' , password='root' , host='127.0.0.3' ,database = DB_name)
# cursor=cnx.cursor()


TABLES ={}



TABLES['deparment']=(
    "create	table deparment("
        "deparment_id int   primary key auto_increment , "
        "created_by int not null ,"
        "name varchar(200) not null ,"
        "deparment_discription varchar(200) not null ,"
        #"deparment_head int not null, "
        #"foreign key(deparment_head) references users(user_id) ,"
	    "status Enum('active' ,'Inactive' ) default 'active' "
        ")ENGINE=InnoDB"
    )


TABLES['users']=(
    "create	table users("
        "user_id int   primary key NOT NULL auto_increment, "
        "f_name varchar(30) not null ,"
        "l_name VARCHAR(50) NOT NULL,"
        "email VARCHAR(100) UNIQUE NOT NULL,"
        "password VARCHAR(255) NOT NULL,"
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "mob_nu char(12) not null , "
	    "department_id int default null ,"
        "role ENUM('employee', 'deparment_head','assets_manager' ) DEFAULT  NULL ,"
	    "foreign key(department_id) references deparment(deparment_id) "
        
        
        ")ENGINE=InnoDB"
    )

TABLES['assets_catagories']=(
    "create	table assets_catagories("
        "catagories_id int   primary key NOT NULL auto_increment, "
        "created_by int not null ,"
        "name varchar(100) not null ,"
        "catagorie_discription varchar(200) not null ,"
	    "created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP "
        ")ENGINE=InnoDB"
    )




TABLES['assets']=(
    "create	table assets("
        "asset_id int   primary key NOT NULL auto_increment, "
        "name varchar(30) not null ,"
	    "category_id int not null, "
        "created_by int not null ,"
        #"Asset Tag varchar(10) UNIQUE NOT NULL "
        
        "aquasition_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,"
	    "allocated_to_deparment int default null ," 
        "allocated_to_employee int default null ,"
        
        "status ENUM('Available', 'Allocated','Reserved' ,'Under_Maintenance', 'Lost' ,'Retired' ,'Disposed' ) DEFAULT  'Available' , "
	    "foreign key(category_id) references assets_catagories(catagories_id) ,"
	    "foreign key(allocated_to_deparment) references deparment(deparment_id),"
        "foreign key(allocated_to_employee) references users(user_id)"
        
        ")ENGINE=InnoDB"
    )



TABLES['resource_booking']=(
    "create	table resource_booking("
        "allocation_id int   primary key auto_increment , "
        "asset_id int not null ,"
        "user_id int not null ,"
	    "allocation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
	   
	    "returning_time TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP  ,"

        "status ENUM('Upcoming', 'Ongoing' , 'Completed' , 'Cancelled') DEFAULT  'Upcoming'  , "
        "foreign key(asset_id) references assets(asset_id) ,"
        "foreign key(user_id) references users(user_id)"
        
        ")ENGINE=InnoDB"
    )


TABLES['maintenance']=(
    "create	table maintenance("
        "maintenance_id int   primary key auto_increment , "
        "asset_id int not null ,"
        "requested_by int not null ,"
	"approved_by int not null ,"
	"requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,"
	"issue_discription varchar(200) not null ,"
        "status ENUM('Pending', 'Approved' , 'Rejected' , 'Technician Assigned') DEFAULT  'pending'  , "
        "foreign key(asset_id) references assets(asset_id),"
        "foreign key(requested_by) references users(user_id),"
	"foreign key(approved_by) references users(user_id)"
        
        ")ENGINE=InnoDB"
    )



def create_database(cursor):
    try:
        cursor.execute(
            f"create database {DB_name}  "
        )
    except mysql.connector.Error as err:
        print(f"failed to create database {DB_name} : {err}")
        exit(1)


def create_tables(TABLES):
    for table_name in TABLES:
        table_discription=TABLES[table_name]
        try:
            print(f"creating table {table_name}")
            cursor.execute(table_discription)
        except mysql.connector.Error as err:
            if err.errno==errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"table {table_name} alredy exist")
            else:
                print(err)
        else:
            print("ok")
    return 0

# def use_database(DB_name , TABLES):
def use_database():
    try:
        cursor.execute(f"use {DB_name}")
        print(f"databse '{DB_name}' is in use ")
        # create_tables(TABLES)
        return True
    except mysql.connector.Error as err:
        print(f"database {DB_name} dosen't exist :{err}")
        if err.errno==errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print(f"database {DB_name} created successfully .")
            use_database()
            create_tables(TABLES)
            cnx.database=DB_name
            return True
        else:
            print(err)
            return False
    



def authenticate_user(email,password):
    try:
        query = ("select password ,user_id ,role from users where email = %s ")
        values=(email ,)
        print(values)
        cursor.execute(query , values)
        result = cursor.fetchone()
        if result == None:
            print("user not excists")
            return 1
        else:
            print(type(result[0]))
            print(password)
            print(type(password))
            print(check_password_hash( result[0],password))
            print("user exists")
            if check_password_hash( result[0],password):
                print('authentication is done')
                return result
            else:
                print("unautherized user")
                return 1

            
    except mysql.connector.Error as err:
        print(err)
        return 1
 

def connection_server():
        try:
            global cnx
            cnx = mysql.connector.connect(user='root' , password='root' , host='127.0.0.3')
            global cursor

            cursor=cnx.cursor()
            return True
        except mysql.connector.errors.DatabaseError as err:
            if err.errno==2003:
                print(err)
                return False

# if __name__ == "__main__":
if connection_server():
    # global cnx
    cnx = mysql.connector.connect(user='root' , password='root' , host='127.0.0.3' )
    # global cursor

    cursor=cnx.cursor()
    use_database()
    print("database setup is complete successfully  ")
else: 
    print("database server is not runnig ")
    exit