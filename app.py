from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
from collections import defaultdict
import connect
import os
from datetime import datetime

app = Flask(__name__)

dbconn = None
connection = None


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/listdrivers")
def listdrivers():
    

    connection = getCursor()
    sql="""SELECT CONCAT(d.surname,' ', d.first_name  ) AS full_name, c.model, d.age, d.driver_id, c.drive_class
 FROM driver d
  INNER JOIN car c on c.car_num = d.car;"""
    
    connection.execute(sql)
    driverList = connection.fetchall()
    print(driverList)
    return render_template("driverlist.html", driver_list = driverList)    

@app.route("/listdrivers/rundetails", methods=["GET"])
def rundetails():

    connection = getCursor()
    sql = "SELECT * FROM driver;"
    connection.execute(sql)
    driverList = connection.fetchall()
    driverid = request.args.get('driver_id')
    connection = getCursor()
    sql = """SELECT d.driver_id, CONCAT(d.surname,' ', d.first_name) AS full_name, c.model, c.drive_class, r.run_num, r.seconds, r.cones, r.wd, crs.name
 FROM driver d
  INNER JOIN car c on c.car_num = d.car
   INNER JOIN run r on d.driver_id = r.dr_id
    INNER JOIN course crs on  crs.course_id = r.crs_id WHERE driver_id = %s;"""
    parameters = (driverid,)
    connection.execute(sql,parameters)
    driverRunDetail = connection.fetchall()
    print(driverRunDetail)
    return render_template("rundetails.html", driver_run_detail = driverRunDetail, driver_list = driverList)  

@app.route("/listcourses")
def listcourses():

    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courses = connection.fetchall()

    #indicating whether the file is an image or not
    list_of_courses = []
    for course in courses:
        course_id, course_name, filename = course
        _, file_extension = os.path.splitext(filename)
        is_image = file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif']
        list_of_courses.append((course_id, course_name, filename, is_image))

    return render_template("courselist.html", course_list=list_of_courses)

@app.route("/graph")
def showgraph():
   
   connection = getCursor()
   sql = """SELECT d.driver_id, CONCAT(d.surname,' ', d.first_name) AS full_name, c.model, c.drive_class, r.run_num, r.seconds, r.cones, r.wd, crs.name, d.age
    FROM driver d
    INNER JOIN car c on c.car_num = d.car
    INNER JOIN run r on d.driver_id = r.dr_id
    INNER JOIN course crs on crs.course_id = r.crs_id;"""

   connection.execute(sql)
   overallResults = connection.fetchall()
  
   unique_drivers = {}  

   for result in overallResults:
        driver_id = result[0]
        full_name = result[1]
        car_model = result[2]
        course_name = result[8]
        age = result[9]
        seconds = result[5] or 0
        cones = result[6] or 0
        wd = result[7] or 0
        run_total = seconds + cones * 5 + wd * 10
        course_time = run_total if run_total != 0 else float('inf')
        

        if driver_id not in unique_drivers:
          unique_drivers[driver_id] = {'full_name': full_name, 'car_model': car_model, 'results': {}}

        if course_name not in unique_drivers[driver_id]['results']:
        # If no previous run for this course, store the current run_total
          unique_drivers[driver_id]['results'][course_name] = course_time
        else:
        # Compare the current run_total with the previous run_total
          unique_drivers[driver_id]['results'][course_name] = min(unique_drivers[driver_id]['results'][course_name], course_time
        )

   newResults = []
   

   for driver_id, driver_data in unique_drivers.items():
    full_name = driver_data['full_name']
    car_model = driver_data['car_model']
    driver_info = driver_data['results']

    overall_time_display = "DNF"

    # Check if all runs are not "DNF" or float('inf') for each course
    if all(time != "DNF" and time != float('inf') for time in driver_info.values()):
        # Calculate overall time considering numeric values
        overall_time = round(sum(float(time) for time in driver_info.values()), 2)
        overall_time_display = overall_time
    else:
        overall_time_display = "DNF"

    for key, value in driver_info.items():
        if value == float('inf'):
            driver_info[key] = 'DNF'

    newResults.append((driver_id, full_name, overall_time_display)) 
    
   
    # Sort newResults by overall time
   newResults.sort(key=lambda x: float('inf') if x[2] == 'DNF' else float(x[2]))

   driver_list =[]

   for idx, result in enumerate(newResults):
         if result[2] != "DNF":
            if 0 <= idx < 5:
                driver_list.append(result) 
    
   bestDriverList = [' '.join([str(item[0]), item[1]]) for item in driver_list]  
   resultsList = [item[2] for item in driver_list]

   print(bestDriverList)
   print(resultsList)

   return render_template("top5graph.html", name_list = bestDriverList, value_list = resultsList)




@app.route("/results")
def overallresults():

   connection = getCursor()
   sql = """SELECT d.driver_id, CONCAT(d.surname,' ', d.first_name) AS full_name, c.model, c.drive_class, r.run_num, r.seconds, r.cones, r.wd, crs.name, d.age
    FROM driver d
    INNER JOIN car c on c.car_num = d.car
    INNER JOIN run r on d.driver_id = r.dr_id
    INNER JOIN course crs on crs.course_id = r.crs_id;"""

   connection.execute(sql)
   overallResults = connection.fetchall()
  

   unique_drivers = {}  

   for result in overallResults:
        driver_id = result[0]
        full_name = result[1]
        car_model = result[2]
        course_name = result[8]
        age = result[9]
        seconds = result[5] or 0
        cones = result[6] or 0
        wd = result[7] or 0
        run_total = seconds + cones * 5 + wd * 10
        course_time = run_total if run_total != 0 else float('inf')
        
        if age is not None and 12 <= age <= 25:
           full_name = full_name + " (J)"

        if driver_id not in unique_drivers:
          unique_drivers[driver_id] = {'full_name': full_name, 'car_model': car_model, 'results': {}}

        if course_name not in unique_drivers[driver_id]['results']:
        # If no previous run for this course, store the current run_total
          unique_drivers[driver_id]['results'][course_name] = course_time
        else:
        # Compare the current run_total with the previous run_total
          unique_drivers[driver_id]['results'][course_name] = min(unique_drivers[driver_id]['results'][course_name], course_time
        )

   newResults = []
   

   for driver_id, driver_data in unique_drivers.items():
    full_name = driver_data['full_name']
    car_model = driver_data['car_model']
    driver_info = driver_data['results']

    overall_time_display = "DNF"

    # Check if all runs are not "DNF" or float for each course
    if all(time != "DNF" and time != float('inf') for time in driver_info.values()):
        overall_time = round(sum(float(time) for time in driver_info.values()), 2)
        overall_time_display = overall_time
    else:
        overall_time_display = "DNF"

    for key, value in driver_info.items():
        if value == float('inf'):
            driver_info[key] = 'DNF'

    newResults.append((driver_id, full_name, car_model, driver_info.get("Going Loopy", ""),driver_info.get("Mum's Favourite", ""), driver_info.get("Walnut", ""), driver_info.get("Hamburger", ""), driver_info.get("Shoulders Back", ""),driver_info.get("Cracked Fluorescent", ""), overall_time_display)) 
    
   
    # Sort newResults by overall time
   newResults.sort(key=lambda x: float('inf') if x[9] == 'DNF' else float(x[9]))

   
   driver_list =[]

   for idx, result in enumerate(newResults):
         if result[9] != "DNF":
            if idx == 0:
                driver_list.append((*result, "Cup 🏆" )) 
            elif 0 < idx < 5:
                driver_list.append((*result, "Prize 🎖️")) 
            elif idx >= 5:
                driver_list.append((*result, ""))
         elif result[9] == "DNF":
             driver_list.append((*result,"NQ"))
             
   
   return render_template("overallresults.html", driver_list=driver_list)

@app.route("/admin")
def dashboard():

  return render_template("dashboard.html") 

@app.route("/error")
def error():

  return render_template("error.html") 


@app.route("/admin/juniorlist")
def listjuniordrivers():
   connection = getCursor()
   sql = """SELECT d.driver_id, CONCAT(d.surname,' ', d.first_name) AS driver_name, d.age, CONCAT(dd.surname, ' ', dd.first_name) AS caregiver, c.model, c.drive_class FROM driver d
LEFT JOIN 
    driver dd ON dd.driver_id = d.caregiver
INNER JOIN 
    car c ON c.car_num = d.car
WHERE 
    d.age BETWEEN 12 AND 25
ORDER BY 
    d.age DESC, d.surname;

   """
   connection.execute(sql)
   juniorList = connection.fetchall()
   
   return render_template("juniorlist.html", juniorList = juniorList) 


def searchresults(keywords):
   
   connection = getCursor()
   if keywords:
     sql= """SELECT d.driver_id, CONCAT(d.surname,' ', d.first_name) AS full_name, d.age,c.model, c.drive_class, r.run_num, r.seconds, r.cones, r.wd, crs.name
    FROM driver d
    INNER JOIN car c on c.car_num = d.car
    INNER JOIN run r on d.driver_id = r.dr_id
    INNER JOIN course crs on crs.course_id = r.crs_id WHERE surname LIKE %s OR first_name LIKE %s;"""
     keywords = '%' + keywords + '%'
     connection.execute(sql, (keywords, keywords))
   else:
      sql = """
        SELECT driver_id, surname, first_name, age, caregiver 
        FROM driver;
        """
      connection.execute(sql)


   driver_results= connection.fetchall()

   return driver_results



@app.route("/admin/search", methods=["GET", "POST"])

def searchdrivers():
   search_results = []
   keywords = ""
   
   if request.method == "POST":
        keywords = request.form['search']
        if keywords:  
            search_results = searchresults(keywords)
   else:
        search_results = []

   return render_template("searchresults.html", search_results = search_results, keywords = keywords) 



@app.route("/admin/editruns", methods=["GET", "POST"])
def editruns(): 

  try: 
     connection = getCursor()
     sql= """SELECT DISTINCT dr_id FROM run;"""
     connection.execute(sql)
     driverIdList = connection.fetchall()
     sql= """SELECT DISTINCT crs_id FROM run;"""
     connection.execute(sql)
     courseIdList = connection.fetchall()
     sql= """SELECT DISTINCT run_num FROM run;"""
     connection.execute(sql)
     runNumList = connection.fetchall()

     sql= """SELECT d.driver_id, CONCAT(d.surname,' ', d.first_name) AS full_name"""
   
     dr_id = request.form.get('dr_id')
     crs_id = request.form.get('crs_id')
     run_num = request.form.get('run_num')
     seconds = request.form.get('seconds')
     cones = request.form.get('cones')
     wd = request.form.get('wd')

     # Check if seconds is not null
     sql = """SELECT seconds FROM run WHERE dr_id = %s AND crs_id = %s AND run_num = %s;"""
     connection.execute(sql, (dr_id, crs_id, run_num))
     check_seconds = connection.fetchone()

     if check_seconds and check_seconds[0] is not None:
      error_message = "Run details cannot be edited twice!!"
      return render_template("error.html", error_message=error_message)
     else:
      sql = """UPDATE run SET seconds = %s, cones = %s, wd = %s WHERE dr_id = %s AND crs_id = %s AND run_num = %s;"""
      parameters = (seconds, cones, wd, dr_id, crs_id, run_num)
      cur = getCursor()
      cur.execute(sql, parameters)

      return render_template("editruns.html", driver_id_list= driverIdList, course_id_list = courseIdList, run_num_list = runNumList) 
     

  # Handle the exception

  except Exception as e:
    error_message = f"An error occurred: {str(e)}"
    return render_template("error.html", error_message=error_message)

 

@app.route("/admin/adddrivers", methods=['GET', 'POST'])
def adddrivers():
 
  if request.method == 'POST':
      is_junior = request.form.get('is_junior') == 'on'
      if is_junior:
        return redirect(url_for('addjuniordrivers'))
      else:
        return redirect(url_for('addadriver'))

  return render_template('adddrivers.html')

@app.route("/admin/adddrivers/success")
def success():
    return render_template("success.html", message="Driver successfully added!")


@app.route("/admin/adddrivers/addadriver", methods=["GET", "POST"])
def addadriver():
   
 try:  
   connection = getCursor()
   sql= """SELECT car_num FROM car;"""
   connection.execute(sql)
   carNumList = connection.fetchall()
   sql= """SELECT driver_id FROM driver;"""
   connection.execute(sql)
   driverIdList = connection.fetchall()

   dr_id= request.form.get('dr_id')
   driver_id = request.form.get('driver_id')
   first_name = request.form.get('first_name')
   surname = request.form.get('surname')

   # Check if dr_id exists in the car table
   check_car_id= """SELECT car_num FROM car WHERE car_num = %s;"""
   connection.execute(check_car_id, (dr_id,))
   car_result = connection.fetchone()
 
   if car_result:

    # Insert the driver data into the driver 
     sql= """INSERT INTO driver (first_name, surname, car) VALUES (%s, %s, %s);"""
     parameters = (first_name, surname, dr_id)
     connection.execute(sql, parameters)

     new_id = connection.lastrowid

     sql= """INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'A', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'A', 2, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'B', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'B', 2, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'C', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'C', 2, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'D', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'D', 2, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'E', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'E', 2, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'F', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'F', 2, null, null, 0);"""
     
     connection.execute(sql, (new_id, new_id,new_id, new_id, new_id, new_id, new_id, new_id, new_id, new_id, new_id, new_id,))

     return redirect(url_for('success', message='Driver added successfully!'))
 
 # Handle the exception
 except Exception as e:
   error_message = f"An error occurred: {str(e)}"
   return render_template("error.html", error_message=error_message)
 

 return render_template('addadriver.html', car_num_list = carNumList)


@app.route("/admin/adddrivers/junior", methods=["GET", "POST"])
def addjuniordrivers():
 try:    
   connection = getCursor()
   sql= """SELECT car_num FROM car;"""
   connection.execute(sql)
   carNumList = connection.fetchall()
   
   #filter out the junior drivers
   sql= """SELECT driver_id, CONCAT(surname,' ', first_name) AS full_name FROM driver WHERE age is NULL;"""
   connection.execute(sql)
   driverList = connection.fetchall()


   dr_id= request.form.get('dr_id')
   first_name = request.form.get('first_name')
   surname = request.form.get('surname')

   check_car_id= """SELECT car_num FROM car WHERE car_num = %s;"""
   connection.execute(check_car_id, (dr_id,))
   car_result = connection.fetchone()
   caregiver = request.form.get('caregiver')


   if car_result:
     

     sql= """INSERT INTO driver (first_name, surname, date_of_birth, age, caregiver, car) VALUES (%s, %s, %s, %s, %s, %s);"""
     date_of_birth = request.form.get('date_of_birth') 
     dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
    # Get the current date
     today = datetime.now()
    # Calculate age
     age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
     parameters = (first_name, surname, date_of_birth, age, caregiver, dr_id,)
     connection.execute(sql, parameters)

     print(car_result)

     new_id = connection.lastrowid

     if age < 12 or age >25:  
        error_message = "Not a junior driver! Please enter the correct junior's birthday!!"
        return render_template("error.html", error_message=error_message)
     
     else:

       sql= """INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'A', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'A', 2, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'B', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'B', 2, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'C', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'C', 2, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'D', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'D', 2, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'E', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'E', 2, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'F', 1, null, null, 0);
     INSERT INTO run(dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, 'F', 2, null, null, 0);"""
     
       connection.execute(sql, (new_id, new_id,new_id, new_id,new_id, new_id, new_id, new_id, new_id, new_id,new_id, new_id,))
    
     return redirect(url_for('success', message='Driver added successfully!'))
    
 # Handle the exception
 except Exception as e:
   error_message = f"An error occurred: {str(e)}"
   return render_template("error.html", error_message=error_message)
 return render_template("addjunior.html", driver_list = driverList, car_num_list = carNumList)