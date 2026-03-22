from flask import Flask , render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request,redirect,render_template
from flask import session

app = Flask(__name__)
app.secret_key = "Your_Key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer , primary_key = True)
    first_name = db.Column(db.String(100),nullable = False)
    last_name = db.Column(db.String(100),nullable = False)
    gender = db.Column(db.String(20),nullable = False)
    email = db.Column(db.String(150),nullable = False ,unique = True)
    date_of_birth = db.Column(db.Date,nullable = False)
    username = db.Column(db.String(100),nullable = False,unique = True)
    password = db.Column(db.String(100),nullable = False)
    course = db.Column(db.String(100),nullable = False)
    created_at = db.Column(db.DateTime,default = datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"
@app.route("/")
def index():
    return redirect("/login")

@app.route("/login",methods = ["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username = username).first()
        if user and user.password == password:
            session["user_id"] = user.id
            return redirect("/home")
        else:
            error =  "Invalid Username or password "
    return render_template ("login_page.html",error = error)


@app.route("/register", methods = ["GET","POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("Fname")
        last_name = request.form.get("Lname")
        gender = request.form.get("gender")
        email = request.form.get("email")
        date_of_birth = datetime.strptime(request.form.get("dob"),"%Y-%m-%d")
        username = request.form.get("username")
        password = request.form.get("password")
        course = request.form.get("course")
        existing_user = User.query.filter_by(username = username).first()
        if not first_name or not last_name or not gender or not email or not date_of_birth or not username or not password or not course:
            return render_template("register.html",error = "Fill all the fields")       
        if existing_user:
            return "User already exist! try another username"
        new_user = User(first_name=first_name,
                        last_name = last_name,
                        gender = gender,
                        email = email,
                        date_of_birth = date_of_birth,
                        username = username,
                        password = password,
                        course = course
                        )
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")    
    return render_template ("register.html")



@app.route("/home")
def home():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return render_template("home_page.html",user = user)
    else:
        return redirect("/login")

@app.route("/update/<int:id>",methods = ["GET" , "POST"])
def update(id):
    if "user_id" not in session:
        return redirect("/login")
    if session["user_id"] != id:
        return "Unauthorized access"
    
    user = User.query.get(id)
    if request.method == "POST":
        fullname = request.form["fullname"]
        names = fullname.split()
        if len(names)>1:
            user.last_name = names[1]
        else:
            user.last_name = ""
        user.gender = request.form["gender"]
        user.email = request.form["email"]
        user.date_of_birth = datetime.strptime(request.form["dob"],"%Y-%m-%d")
        user.course = request.form["course"]
        db.session.commit()
        return redirect("/home")
    return render_template("update.html",user=user)

@app.route("/update_succs")
def updateSuccs():
    return render_template("update_succs.html")

@app.route("/delete/<int:id>",methods = ["POST"])
def delete(id):
    if "user_id" not in session:
        return redirect("/login")
    if session["user_id"]!=id:
        return "Unauthorized access!"
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    session.pop("user_id",None)
    return render_template("delete.html")

@app.route("/logout",methods = ["POST"])
def logout():
    session.pop("user_id",None)
    return redirect("/login")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

