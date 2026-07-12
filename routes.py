from flask import Flask , request , render_template , redirect , url_for, session , flash
import models 
import config

app = Flask(__name__)
app.secret_key=config.secret_key

@app.route('/')
def welcome():
    if models.connection_server():
        if  models.cnx:
            models.use_database()
            print('database is created  and connected ')
            session['db_status']=True
            return redirect(url_for('login'))
        else:
            return "some technical essues is there may be tables are not created  "
    else: 
        session['db_status']=False
        flash("database server is not connected ")
        return render_template("error.html")
    


@app.route('/signup' , methods=['POST','GET'])
def signup():
    if not session.get('db_status'):
        return redirect(url_for('welcome'))
    if session.get('role')=='employee':
        session.clear()
        return redirect(url_for('signup'))
    

    if request.method=="POST":
        first_name = request.form.get("fr_name")
        last_name = request.form.get("la_name")
        email = request.form.get("email")
        password = request.form.get("password")
        mob_nu = request.form.get("mob_num")
        if any(not x or str(x).strip() == "" for x in [first_name , last_name , email , password, mob_nu ]):
            flash("submited empty data !!")
            return redirect(url_for('signup'))
        try:
            password = models.generate_password_hash(password)
            query= "insert into users (f_name   , l_name  , email  , password  , mob_nu  ) values (%s ,%s ,%s ,%s,%s)"
            values= (first_name , last_name , email , password , mob_nu )
            models.cursor.execute(query , values )
            models.cnx.commit()
            return redirect(url_for("login"))
        except models.mysql.connector.Error as err:
            if err.errno== 1062:
                print("error code 1062")
                return render_template("signup.html" , data="user exists")
            else:
                print(err)
                return render_template("signup.html")

    else:
        return render_template("signup.html")
   
        

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        email =request.form.get("email")
        password = request.form.get('password')
        if email=="admin@gmail.com" and password == "admin123":
            session['user_id']='0'
            session['role']= 'admin'
            return redirect(url_for('dashboard'))

        result = models.authenticate_user(email, password)
        if result !=1:
            print(result[1])
            session['user_id']=result[1]
            session['role']= result[2]
            return redirect(url_for('dashboard'))
        else:
            flash("user is not exist")
            return render_template("login.html", data="Invalid email or password")
    else:
        
        return render_template("login.html")
    
@app.route('/dashboard', methods=['POST' , "GET"])
def dashboard():
    if session.get('user_id'):
        print(session.get('user_id'))
        role = session.get('role')
        if role=="admin":
            return redirect(url_for('admin_dashboard'))
        elif role=="employee":
            return redirect(url_for('employee_dashboard'))
        elif role=="deparment_head":
            return redirect(url_for('deparment_head_dashboard'))
        elif role=="assets_manager":
            return redirect(url_for('assets_manager_dashboard'))
        else:
            flash("role is not exist")
            return render_template("login.html", data="may be role is not assigned yet")
    else:
        return redirect(url_for('login'))
@app.route('/logout', methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for('welcome'))

@app.route('/employee_dashboard')
def employee_dashboard():
    if session.get('role')=='employee':
        return "wellcom to employee dashboard"
        # return render_template("procurment_dashboard.html")
    else:
        return redirect(url_for('dashboard'))
    

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role')=='admin':
        # return "wellcom to admin dashboard"
        return render_template("admin_dashboard.html")
    else:
        return redirect(url_for('dashboard'))
    
@app.route('/deparment_head_dashboard')
def deparment_head_dashboard():
    if session.get('role')=='deparment_head':
        return "wellcom to deparment_head_dashboard"
        # return render_template("vendor_dashboard.html")
    else:
        return redirect(url_for('dashboard'))

   
@app.route('/assets_manager_dashboard')
def assets_manager_dashboard():
    if session.get('role')=='assets_manager':
        # return "wellcom to assets_manager_dashboard"
        return render_template("asset_manager_dashboard.html")
    else:
        return redirect(url_for('dashboard'))



@app.route('/users' ,methods=['POST' ,'GET'])
def users():
    if session.get('role')=='admin' :
        session.get("user_id")
        try:
            query=(" select user_id ,f_name ,email ,created_at ,mob_nu , department_id , role from users ")
            models.cursor.execute(query )
            result = models.cursor.fetchall()
            print(result)
            if result:
                return render_template('admin_dashboard.html' , result=result , users = result)
            else:
                flash(" there is no users available . !!!")
                return redirect(url_for('dashboard'))
        except models.mysql.connector.Error as err:
                print(err)
                return "something goes wronge while fething rfqs"
    # elif session.get('role')=='vendor':
    #     try:
    #         query=(" select rfq_id ,requested_by ,deadline ,item_name ,qty , discription , categery   from rfqs where status = 'pending' ")
    #         models.cursor.execute(query )
    #         result = models.cursor.fetchall()
    #         print(result)
    #         if result:
    #             return render_template('pending_rfqs.html' , result=result)
    #         else:
    #             flash(" there is no requests available . !!!")
    #             return redirect(url_for('dashboard'))
    #     except models.mysql.connector.Error as err:
    #             print(err)
    #             return "something goes wronge while fething rfqs"

    else:
        return redirect(url_for('login'))



@app.route('/departments' ,methods=['POST' ,'GET'])
def departments():
    if session.get('role')=='admin' :
        # session.get("user_id")
        try:
            query=(" select deparment_id ,deparment_discription ,name ,status  from deparment ")
            models.cursor.execute(query )
            result = models.cursor.fetchall()
            print(result)
            if result:
                return render_template('admin_dashboard.html' , result=result)
            else:
                flash(" there is no departments available . !!!")
                return redirect(url_for('dashboard'))
        except models.mysql.connector.Error as err:
                print(err)
                return "something goes wronge while fething rfqs"
    # elif session.get('role')=='vendor':
    #     try:
    #         query=(" select rfq_id ,requested_by ,deadline ,item_name ,qty , discription , categery   from rfqs where status = 'pending' ")
    #         models.cursor.execute(query )
    #         result = models.cursor.fetchall()
    #         print(result)
    #         if result:
    #             return render_template('pending_rfqs.html' , result=result)
    #         else:
    #             flash(" there is no requests available . !!!")
    #             return redirect(url_for('dashboard'))
    #     except models.mysql.connector.Error as err:
    #             print(err)
    #             return "something goes wronge while fething rfqs"

    else:
        return redirect(url_for('login'))


@app.route('/assets_catagories' ,methods=['POST' ,'GET'])
def assets_catagories():
    if session.get('role')=='admin' :
        session.get("user_id")
        try:
            query=(" select catagories_id ,name ,created_at  from assets_catagories ")
            models.cursor.execute(query )
            result = models.cursor.fetchall()
            print(result)
            if result:
                return render_template('admin_dashboard.html' , result=result)
            else:
                flash(" there is no catagories available . !!!")
                return redirect(url_for('dashboard'))
        except models.mysql.connector.Error as err:
                print(err)
                return "something goes wronge while fething rfqs"
    elif session.get('role')=='assets_manager' :
        session.get("user_id")
        try:
            query=(" select catagories_id ,name ,created_at  from assets_catagories ")
            models.cursor.execute(query )
            result = models.cursor.fetchall()
            print(result)
            if result:
                return render_template('asset_manager_dashboard.html' , result=result)
            else:
                flash(" there is no catagories available . !!!")
                return redirect(url_for('dashboard'))
        except models.mysql.connector.Error as err:
                print(err)
                return "something goes wronge while fething rfqs"
    # elif session.get('role')=='vendor':
    #     try:
    #         query=(" select rfq_id ,requested_by ,deadline ,item_name ,qty , discription , categery   from rfqs where status = 'pending' ")
    #         models.cursor.execute(query )
    #         result = models.cursor.fetchall()
    #         print(result)
    #         if result:
    #             return render_template('pending_rfqs.html' , result=result)
    #         else:
    #             flash(" there is no requests available . !!!")
    #             return redirect(url_for('dashboard'))
    #     except models.mysql.connector.Error as err:
    #             print(err)
    #             return "something goes wronge while fething rfqs"

    else:
        return redirect(url_for('login'))



@app.route('/create_catagories' ,methods=['POST' ,'GET'])
def create_catagories():
    if  session.get('role') =='admin' :
        if request.method=='POST':
            name = request.form.get('name')
            discription = request.form.get('catagorie_discription')
            if any(not x or str(x).strip() == "" for x in [name , discription ]):
                flash("submited empty data !!")
                return redirect(url_for('dashboard'))
            else:
                try:
                    query=(" insert into assets_catagories (created_by ,name ,catagorie_discription) values (%s , %s ,%s)")
                    values=( session.get("user_id") , name , discription )
                    models.cursor.execute(query , values)
                    models.cnx.commit()
                    return redirect(url_for('dashboard'))
                except models.mysql.connector.Error as err:
                    print(err)
                    return "something goes wrong"
        else:
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))



@app.route('/add_assets' ,methods=['POST' ,'GET'])
def add_assets():
    if  session.get('role') =='assets_manager' :
        if request.method=='POST':
            name = request.form.get('name')
            category_id = request.form.get('category_id')
            if any(not x or str(x).strip() == "" for x in [name , category_id ]):
                flash("submited empty data !!")
                return redirect(url_for('dashboard'))
            else:
                try:
                    query=(" insert into assets (created_by ,name ,category_id) values (%s , %s ,%s)")
                    values=( session.get("user_id") , name , category_id )
                    models.cursor.execute(query , values)
                    models.cnx.commit()
                    return redirect(url_for('dashboard'))
                except models.mysql.connector.Error as err:
                    print(err)
                    return "something goes wrong"
        else:
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))


@app.route('/assets' ,methods=['POST' ,'GET'])
def assets():
    if session.get('role')=='admin' :
        session.get("user_id")
        try:
            query=(" select asset_id ,name ,category_id , created_by , aquasition_date , allocated_to , status  from assets ")
            models.cursor.execute(query )
            result = models.cursor.fetchall()
            print(result)
            if result:
                return render_template('admin_dashboard.html' , result=result)
            else:
                flash(" there is no catagories available . !!!")
                return redirect(url_for('dashboard'))
        except models.mysql.connector.Error as err:
                print(err)
                return "something goes wronge while fething rfqs"
    elif session.get('role')=='assets_manager' :
        session.get("user_id")
        try:
            query=(" select asset_id ,name ,category_id , created_by , aquasition_date , allocated_to , status  from assets ")
            models.cursor.execute(query )
            result = models.cursor.fetchall()
            print(result)
            if result:
                return render_template('asset_manager_dashboard.html' , result=result)
            else:
                flash(" there is no catagories available . !!!")
                return redirect(url_for('dashboard'))
        except models.mysql.connector.Error as err:
                print(err)
                return "something goes wronge while fething rfqs"
    # elif session.get('role')=='vendor':
    #     try:
    #         query=(" select rfq_id ,requested_by ,deadline ,item_name ,qty , discription , categery   from rfqs where status = 'pending' ")
    #         models.cursor.execute(query )
    #         result = models.cursor.fetchall()
    #         print(result)
    #         if result:
    #             return render_template('pending_rfqs.html' , result=result)
    #         else:
    #             flash(" there is no requests available . !!!")
    #             return redirect(url_for('dashboard'))
    #     except models.mysql.connector.Error as err:
    #             print(err)
    #             return "something goes wronge while fething rfqs"

    else:
        return redirect(url_for('login'))


@app.route('/allocate_roles' ,methods=['POST' ,'GET'])
def allocate_roles():
    if  session.get('role') =='admin' :
        if request.method=='POST':
            D_id = request.form.get('department_id')
            role = request.form.get('role')
            user_id = request.form.get('user_id')

            if any(not x or str(x).strip() == "" for x in [D_id , role , user_id ]):
                flash("submited empty data !!")
                return redirect(url_for('dashboard'))
            else:
                try:
                    query=(" update users set role =%s  , department_id = %s where user_id = %s")
                    values=(  role , D_id , user_id )
                    models.cursor.execute(query , values)
                    models.cnx.commit()
                    return redirect(url_for('dashboard'))
                except models.mysql.connector.Error as err:
                    print(err)
                    return "something goes wrong"
        else:
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))




@app.route('/allocate_assets_to_deparment' ,methods=['POST' ,'GET'])
def allocate_assets_to_deparment():
    if  session.get('role') =='assets_manager' :
        if request.method=='POST':
            asset_id = request.form.get('asset_id')
            deprtment_id = request.form.get('deprtment_id')

            if any(not x or str(x).strip() == "" for x in [asset_id , deprtment_id ]):
                flash("submited empty data !!")
                return redirect(url_for('dashboard'))
            
            else:
                try:
                    query=(" select status , allocated_to from assets where asset_id = %s")
                    values=(   asset_id  , )
                    models.cursor.execute(query , values)
                    result = models.cursor.fetchone()
                    print(result)
                    if result:
                        if result[0] =='Available' and result[1]==None:
                            query=(" update assets set allocated_to =%s  , status = 'Allocated' where asset_id = %s")
                            values=(  deprtment_id , asset_id   )
                            models.cursor.execute(query , values)
                            models.cnx.commit()
                            return redirect(url_for('dashboard'))
                        elif result[0] =='Reserved' :
                            return "Reserved for futur use"
                        elif result[0] =='Allocated' and result[1]  :
                            return f"allocated already Allocated to department {result[1]}"
                        elif result[0] =='Under_Maintenance' :
                            return "Under_Maintenance"
                        else:
                            return "asste is no more sory"
                    else:
                        return "there is no assets"

                except models.mysql.connector.Error as err:
                    print(err)
                    return "something goes wrong"
        else:
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))









@app.route('/create_department' ,methods=['POST' ,'GET'])
def create_department():
    if  session.get('role') =='admin' :
        if request.method=='POST':
            name = request.form.get('name')
            discription = request.form.get('deparment_discription')
            deparment_head = request.form.get('deparment_head')
            if any(not x or str(x).strip() == "" for x in [name , discription ,deparment_head ]):
                flash("submited empty data !!")
                return redirect(url_for('dashboard'))
            else:
                try:
                    query=(" insert into deparment (created_by ,name ,deparment_discription , deparment_head) values (%s , %s ,%s ,%s)")
                    values=( session.get("user_id") , name , discription ,deparment_head )
                    models.cursor.execute(query , values)
                    models.cnx.commit()
                    return redirect(url_for('dashboard'))
                except models.mysql.connector.Error as err:
                    print(err)
                    return "something goes wrong"
        else:
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
