# Flask

To run this project, you will need MySQL and Python installed in your device.

To installed all the required libraries, use command pip install -r requirements.txt

Also mention your database details in db.yaml

In your database, create 3 tables : 

1. UsersDetails(email VARCHAR(120) PRIMARY KEY, first_name VARCHAR(50) NOT NULL, last_name VARCHAR(50) NOT NULL, city VARCHAR(50) NOT NULL, phone VARCHAR(15) NOT NULL, password VARCHAR(150) NOT NULL)

2. Recipes(blog_id VARCHAR(12) PRIMARY KEY, title VARCHAR(100) NOT NULL, description TEXT NOT NULL, ingredients MEDIUMTEXT NOT NULL, INSTRUCTION MEDIUMTEXT NOT NULL, email VARCHAR(120), FOREIGN KEY(email) REFERENCES UserDetails(email));
