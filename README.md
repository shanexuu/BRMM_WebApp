# BRMM_WebApp Report

## 📊 Web Application Structure (Diagram)

<img width="2163" alt="Structure" src="https://github.com/shanexuu/BRMM_WebApp/assets/139763196/d4b35250-cc76-4d9e-b2fd-f042169dfdfc">

### 💭 Assumptions and 💡 Design Decisions


#### 👤 User Roles

This web application assumes the existence of multiple user roles, there are regular users and administrators. Regular users might have access to basic functionality of this web application, which is public to everyone. Administrators have access the editing, searching and creating interfaces. 

Consequently, to follow a clear and logical pattern, I decided to separate two distinct routes for those two user roles: a route for regular users (e.g. /listdrivers) and a route for admin users (e.g. /admin/dashboard). Routes were organized hierarchically, admin-related routes were nested under /admin, ensuring a logical and predictable URL structure. 
I set up nested routes where data had multiple levels of hierarchy. For example, when users check the driver id of 120's run details, the route might be: /listdrivers/rundetails?driver_id=120

There are two layout templates: base.html and admin.html. Regular users' templates extend base.html (e.g. driverlist.html extends the base.html). Admin Users' template extends admin.html (e.g. editruns.html extends the admin.html).  In my setup, base.html provides the basic structure for all user's side pages, it includes a banner, admin button, navigation bar and footer. However, the structure and layout of admin.html is different from base.html. I want to keep the layout of admin pages to be clean and easy to navigate, I divided the layout into left and right, left part is the navigation bar, and I set the position to be fixed, even if the page is scrolled, it still stays in the same position. It enherences user experience for admin users, especially when they are handling large data, it saves time without scrolling up and down.


#### 📱 Responsive Design Considerations

I assumed that users would access this web application from multiple devices, including desktops, laptops, tablets, and smartphones. In order to provide a seamless and user-friendly experience, the responsive design should be considered.


I used Bootstrap to implement a responsive web design approach. for example, when I was designing the nav bar, I added 'navbar-expand-lg' class to control the navigation bar's responsiveness, in this case, it will collapse the navbar when users are browsing on smaller screens. In this app, I used tables to display the lists of drivers, courses and run details, it's necessary to add responsiveness to the tables. In Bootstrap, the 'table-responsive' class enables tables to be responsive.


#### ❌ Error Handling

I assumed that the admin may accidentally insert invalid or incorrect valves to the database, in order to ensure data integrity and accuracy, it's crucial to add error handing to this web app. For handling errors in this project, I considered two aspects: user input validation and Data legitimacy issues. 

User input validation: Before updating or inserting data into the database, it's necessary to check data formats and types. For example, in the editing functionality, cones and WD should be digit, in the input field, I add the attribute of "pattern='\d+'", this means that  the input field should only accept numeric digits. If the admin enters anything other than numbers, the form will not be submitted, and the admin will see a validation error message instead.


Data legitimacy issues: although the user input may match the data formats or types, we still need to consider the accuracy of this data before inserting it into the database. So, I set up an error.html template, adding "render_template("error.html", error_message=error_message)" to the python file. For example, in this project, the junior driver's age is between 12 and 25, if the admin's input is either more than 25 or less than 12, the admin will redirect to an error page that displays "Not a junior driver! Please enter the correct junior's birthday!!", and the data will not be allowed insert into the database. 


## ❓ Database Questions

#### 1. What SQL statement creates the car table and defines its three fields/columns?

CREATE TABLE IF NOT EXISTS car
(
car_num INT PRIMARY KEY NOT NULL,
model VARCHAR(20) NOT NULL,
drive_class VARCHAR(3) NOT NULL
);

#### 2. Which line of SQL code sets up the relationship between the car and driver tables?

FOREIGN KEY (car) REFERENCES car(car_num)

#### 3. Which 3 lines of SQL code insert the Mini and GR Yaris details into the car table?

INSERT INTO car VALUES
(11,'Mini','FWD'),
(17,'GR Yaris','4WD')

#### 4. Suppose the club wanted to set a default value of ‘RWD’ for the driver_class field. What specific change would you need to make to the SQL to do this? (Do not implement this change in your app.)

CREATE TABLE IF NOT EXISTS car (
    car_num INT PRIMARY KEY NOT NULL,
    model VARCHAR(20) NOT NULL,
    drive_class VARCHAR(3) DEFAULT 'RWD' NOT NULL
);


#### 5. Suppose logins were implemented. Why is it important for drivers and the club admin to access different routes? As part of your answer, give two specific examples of problems that could occur if all of the web app facilities were available to everyone.

If drivers and admin are sharing the same routes, it means that drivers have the permissions to edit and insert data into the database. There are two main problems may occur: data privacy issues and data accuracy.

1. Data Privacy: Drivers may access the other driver's sensitive information such as contact details, date of birth, password etc. This might lead to lead to privacy breaches and unsolicited communications.


2. Data Accuracy: Drivers can update and insert data into data without authorisation, which may lead to inaccurate records. For example, any driver can edit their run details to improve their good results, which leads to unfair competition. 

To address these concerns, it's necessary to build different routes for drivers and amin.

## 🌅 Image Sources

banner.jpg: Photo by Kritsada Seekham on Pexels.
driver_list.jpg: Photo by Leif Bergerson on Pexels.
course.jpg: Photo by Hyundai Motor Group on Pexels.
graph.jpg: Photo by Oleksandr P on Pexels.
results.jpg: Photo by Chris Liverani on Unsplash.

