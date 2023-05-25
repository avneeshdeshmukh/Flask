from flask import Flask, render_template, request, redirect,session, url_for, make_response, abort, flash
from flask_bcrypt import Bcrypt
import yaml
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import pymysql
import base64
import functions


db = yaml.safe_load(open('db.yaml'))
app = Flask(__name__,static_url_path='/static')
dbcon = pymysql.connect(host=db['mysql_host'], user=db['mysql_user'],
                        password=db['mysql_password'], db=db['mysql_db'])
bcrypt = Bcrypt(app)
app.secret_key=db['secret_key']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, email, password):
        self.id = email
        self.email = email
        self.password = password

    @staticmethod
    def get(user_id):
        cursor = dbcon.cursor()
        cursor.execute(f"SELECT * FROM UserDetails WHERE email='{user_id}'")
        result = cursor.fetchone()
        cursor.close()

        if result:
            return User(result[0], result[5])  
        return None

@app.route('/')
def home():
    # Fetch user's uploaded blogs
    if(current_user.is_authenticated):

        email=current_user.id
        cur = dbcon.cursor()
        cur.execute(f"SELECT * FROM Recipes")
        recipes = cur.fetchall()
        cur.execute(f"SELECT * FROM UserDetails WHERE email='{email}'")
        user_data=cur.fetchone()
        cur.close()
        return render_template('home.html', recipes=recipes, user=current_user, user_data=user_data)
    else:
        cur = dbcon.cursor()
        cur.execute(f"SELECT * FROM Recipes")
        recipes = cur.fetchall()
        cur.close()
        return render_template('home.html', recipes=recipes, user=current_user, title='Home')

@app.route('/create_recipe', methods=['GET', 'POST'])
@login_required
def create_recipe():
    if request.method == 'POST':
        blog_id=functions.generate_user_id()
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        email=current_user.id
        cursor = dbcon.cursor()
        
        cursor.execute(f"INSERT INTO Recipes (blog_id, title, description, ingredients, INSTRUCTION, email) VALUES ('{blog_id}', '{title}','{description}', '{ingredients}','{instructions}', '{email}')")
        dbcon.commit()
        cursor.close()
        
        # Redirect to a success page or do something else
        return redirect(url_for('home', title='Home'))
    
    # Render the create recipe form template
    return render_template('create_blog.html', user=current_user, title='Share Your Recipe')


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/recipe/<blog_id>')
@login_required
def recipe(blog_id):
    cur=dbcon.cursor()
    cur.execute(f"SELECT * FROM Recipes WHERE blog_id='{blog_id}'")
    blog=cur.fetchone()
    cur.execute(f"SELECT UserDetails.email, UserDetails.first_name, UserDetails.last_name FROM UserDetails NATURAL JOIN Recipes")
    user=cur.fetchone()
    cur.close
    
    if blog is None:
        abort(404)
    
    return render_template('blog.html', blog=blog, users=user, user=current_user, title=blog[1])
        

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        UserDetails = request.form
        first_name = UserDetails['first_name']
        last_name = UserDetails['last_name']
        email = UserDetails['email']
        city = UserDetails['city']
        phone = UserDetails['phone']
        password = bcrypt.generate_password_hash(UserDetails['password']).decode("utf-8")
        cur = dbcon.cursor()
        cur.execute(f"SELECT * FROM UserDetails WHERE email='{email}'")
        check_email=cur.fetchone()
        if check_email:
            flash("Email already taken")
            render_template('signup.html', user=current_user, title='Sign Up')
        else:
            cur.execute(f"INSERT INTO UserDetails(email, first_name, last_name, city, phone, password) VALUES('{email}','{first_name}','{last_name}','{city}','{phone}','{password}')")
            dbcon.commit()
            cur.close()
            return redirect('/login')
        
        dbcon.commit()
        cur.close()
    return render_template('signup.html', user=current_user, title='Sign Up')


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        psw = request.form.get('password')
        
        user = User.get(email)
        if user and bcrypt.check_password_hash(
                user.password, psw
            ):
            login_user(user)
            session['email'] = email
            return redirect(url_for('home'))
        else:
            flash("Wrong Email Or Password")
            return render_template('login.html', user=current_user, title='Login')
    return render_template('login.html', user=current_user, title='Login')

@app.route('/view_profile')
@login_required
def view_profile():
    email = current_user.id
    cur = dbcon.cursor()
    cur.execute(f"SELECT * FROM UserDetails WHERE email = '{email}'")
    user_data = cur.fetchone()
    cur.execute(f"SELECT * FROM Recipes WHERE email = '{email}'")
    blogs = cur.fetchall()
    cur.close()
    return render_template('view_profile.html', users=user_data, blogs=blogs, user=current_user, title='Profile - '+user_data[1]+' '+user_data[2])

@app.route('/about_us')
def AboutUs():
    return render_template('about_us.html', user=current_user, title='About Us')

@app.route('/developer/<id>')
def developer(id):
    cur=dbcon.cursor()
    cur.execute(f"SELECT * FROM dev WHERE id={id}")
    dev=cur.fetchone()
    return render_template('developer.html', user=current_user, title=dev[0], dev=dev)

@app.route('/edit_recipe/<blog_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(blog_id):
    cursor = dbcon.cursor()
    
    # Retrieve the recipe from the database
    cursor.execute(f"SELECT * FROM Recipes WHERE blog_id = '{blog_id}'")
    recipe = cursor.fetchone()
    
    if not recipe:
        # Recipe not found, handle accordingly (e.g., show an error message)
        return "Recipe not found"
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
    
        
        # Update the recipe in the database
        cursor.execute(f"UPDATE Recipes SET title = '{title}', description = '{description}', ingredients = '{ingredients}', INSTRUCTION = '{instructions}' WHERE blog_id = '{blog_id}'")
        dbcon.commit()
        cursor.close()
        
        # Redirect to a success page or do something else
        return redirect(url_for('view_profile'))
    
    # Render the edit recipe form template with the existing recipe data
    return render_template('edit_recipe.html', user=current_user, blog=recipe, title='Edit Recipe')


@app.route('/delete_recipe/<blog_id>')
@login_required
def delete_recipe(blog_id):
    cursor = dbcon.cursor()
    
    # Retrieve the recipe from the database
    cursor.execute(f"SELECT * FROM Recipes WHERE blog_id = '{blog_id}'")
    recipe = cursor.fetchone()
    
    if not recipe:
        # Recipe not found, handle accordingly (e.g., show an error message)
        return "Recipe not found"
    else:
        cursor.execute(f"DELETE FROM Recipes WHERE blog_id='{blog_id}'")
        dbcon.commit()
        cursor.close()
        return redirect('/view_profile')
    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    
    app.run(debug=True)
