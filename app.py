from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
from pathlib import Path
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development-only-change-this-key")
ROOT = Path(__file__).resolve().parent
DB = ROOT / "academic_resources.db"
UPLOAD_DIR = ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "ppt", "pptx", "txt", "png", "jpg", "jpeg", "zip"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
          role TEXT NOT NULL CHECK(role IN ('student','faculty','admin'))
        );
        CREATE TABLE IF NOT EXISTS materials(
          id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
          subject TEXT NOT NULL, description TEXT, filename TEXT NOT NULL,
          uploaded_by INTEGER NOT NULL, created_at TEXT NOT NULL,
          FOREIGN KEY(uploaded_by) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS assignments(
          id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
          subject TEXT NOT NULL, description TEXT NOT NULL,
          due_date TEXT NOT NULL, created_by INTEGER NOT NULL,
          created_at TEXT NOT NULL,
          FOREIGN KEY(created_by) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS submissions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, assignment_id INTEGER NOT NULL,
          student_id INTEGER NOT NULL, answer TEXT NOT NULL,
          submitted_at TEXT NOT NULL, UNIQUE(assignment_id,student_id),
          FOREIGN KEY(assignment_id) REFERENCES assignments(id),
          FOREIGN KEY(student_id) REFERENCES users(id)
        );
        """)
        demo = [
          ("Demo Student","student@example.com","student123","student"),
          ("Demo Faculty","faculty@example.com","faculty123","faculty"),
          ("Demo Admin","admin@example.com","admin123","admin")
        ]
        for name,email,pw,role in demo:
            exists=con.execute("SELECT id FROM users WHERE email=?",(email,)).fetchone()
            if not exists:
                con.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                            (name,email,generate_password_hash(pw),role))

def login_required(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.","error")
            return redirect(url_for("login"))
        return fn(*args,**kwargs)
    return wrapper

def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args,**kwargs):
            if session.get("role") not in roles:
                flash("You do not have permission to access that page.","error")
                return redirect(url_for("dashboard"))
            return fn(*args,**kwargs)
        return wrapper
    return deco

def allowed_file(name):
    return "." in name and name.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("home.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email","").strip().lower()
        password=request.form.get("password","")
        with db() as con:
            user=con.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
        if user and check_password_hash(user["password"],password):
            session.update(user_id=user["id"],name=user["name"],role=user["role"])
            flash("Welcome back, "+user["name"]+"!","success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.","error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.","success")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    with db() as con:
        materials=con.execute("""SELECT m.*,u.name uploader FROM materials m JOIN users u ON u.id=m.uploaded_by ORDER BY m.id DESC LIMIT 5""").fetchall()
        assignments=con.execute("SELECT * FROM assignments ORDER BY due_date ASC LIMIT 5").fetchall()
        if session["role"]=="student":
            submitted=[r["assignment_id"] for r in con.execute("SELECT assignment_id FROM submissions WHERE student_id=?",(session["user_id"],)).fetchall()]
        else: submitted=[]
        counts={
          "materials":con.execute("SELECT COUNT(*) FROM materials").fetchone()[0],
          "assignments":con.execute("SELECT COUNT(*) FROM assignments").fetchone()[0],
          "users":con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        }
    return render_template("dashboard.html",materials=materials,assignments=assignments,submitted=submitted,counts=counts)

@app.route("/materials")
@login_required
def materials():
    q=request.args.get("q","").strip()
    with db() as con:
        rows=con.execute("""SELECT m.*,u.name uploader FROM materials m JOIN users u ON u.id=m.uploaded_by
          WHERE m.title LIKE ? OR m.subject LIKE ? ORDER BY m.id DESC""",("%"+q+"%","%"+q+"%")).fetchall()
    return render_template("materials.html",materials=rows,q=q)

@app.route("/materials/upload",methods=["GET","POST"])
@role_required("faculty","admin")
def upload_material():
    if request.method=="POST":
        title=request.form.get("title","").strip()
        subject=request.form.get("subject","").strip()
        description=request.form.get("description","").strip()
        file=request.files.get("file")
        if not title or not subject or not file or not file.filename:
            flash("Please complete all required fields and choose a file.","error")
            return render_template("upload_material.html")
        if not allowed_file(file.filename):
            flash("File type not supported. Upload PDF, Office, text, image or ZIP files.","error")
            return render_template("upload_material.html")
        safe=secure_filename(file.filename)
        stored=f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{safe}"
        file.save(UPLOAD_DIR/stored)
        with db() as con:
            con.execute("INSERT INTO materials(title,subject,description,filename,uploaded_by,created_at) VALUES(?,?,?,?,?,?)",
              (title,subject,description,stored,session["user_id"],datetime.now().strftime("%d %b %Y, %I:%M %p")))
        flash("Study material uploaded successfully.","success")
        return redirect(url_for("materials"))
    return render_template("upload_material.html")

@app.route("/materials/download/<int:material_id>")
@login_required
def download_material(material_id):
    with db() as con:
        row=con.execute("SELECT filename FROM materials WHERE id=?",(material_id,)).fetchone()
    if not row:
        flash("Material not found.","error")
        return redirect(url_for("materials"))
    return send_from_directory(UPLOAD_DIR,row["filename"],as_attachment=True)

@app.route("/assignments")
@login_required
def assignments():
    with db() as con:
        rows=con.execute("""SELECT a.*,u.name faculty FROM assignments a JOIN users u ON u.id=a.created_by
          ORDER BY a.due_date ASC""").fetchall()
        if session["role"]=="student":
            submitted=[r["assignment_id"] for r in con.execute("SELECT assignment_id FROM submissions WHERE student_id=?",(session["user_id"],)).fetchall()]
        else: submitted=[]
    return render_template("assignments.html",assignments=rows,submitted=submitted)

@app.route("/assignments/create",methods=["GET","POST"])
@role_required("faculty","admin")
def create_assignment():
    if request.method=="POST":
        title=request.form.get("title","").strip()
        subject=request.form.get("subject","").strip()
        description=request.form.get("description","").strip()
        due=request.form.get("due_date","").strip()
        if not all([title,subject,description,due]):
            flash("Please complete all required fields.","error")
            return render_template("create_assignment.html")
        with db() as con:
            con.execute("INSERT INTO assignments(title,subject,description,due_date,created_by,created_at) VALUES(?,?,?,?,?,?)",
              (title,subject,description,due,session["user_id"],datetime.now().strftime("%d %b %Y, %I:%M %p")))
        flash("Assignment created successfully.","success")
        return redirect(url_for("assignments"))
    return render_template("create_assignment.html")

@app.route("/assignments/<int:assignment_id>/submit",methods=["GET","POST"])
@role_required("student")
def submit_assignment(assignment_id):
    with db() as con:
        assignment=con.execute("SELECT * FROM assignments WHERE id=?",(assignment_id,)).fetchone()
        previous=con.execute("SELECT * FROM submissions WHERE assignment_id=? AND student_id=?",(assignment_id,session["user_id"])).fetchone()
    if not assignment:
        flash("Assignment not found.","error")
        return redirect(url_for("assignments"))
    if request.method=="POST":
        answer=request.form.get("answer","").strip()
        if not answer:
            flash("Please enter your answer or submission note.","error")
            return render_template("submit_assignment.html",assignment=assignment,previous=previous)
        with db() as con:
            con.execute("""INSERT INTO submissions(assignment_id,student_id,answer,submitted_at) VALUES(?,?,?,?)
              ON CONFLICT(assignment_id,student_id) DO UPDATE SET answer=excluded.answer,submitted_at=excluded.submitted_at""",
              (assignment_id,session["user_id"],answer,datetime.now().strftime("%d %b %Y, %I:%M %p")))
        flash("Assignment submitted successfully.","success")
        return redirect(url_for("assignments"))
    return render_template("submit_assignment.html",assignment=assignment,previous=previous)

@app.route("/submissions")
@role_required("faculty","admin")
def submissions():
    with db() as con:
        rows=con.execute("""SELECT s.*,u.name student,a.title assignment,a.subject FROM submissions s
          JOIN users u ON u.id=s.student_id JOIN assignments a ON a.id=s.assignment_id ORDER BY s.id DESC""").fetchall()
    return render_template("submissions.html",submissions=rows)

@app.route("/admin/users")
@role_required("admin")
def users():
    with db() as con:
        rows=con.execute("SELECT id,name,email,role FROM users ORDER BY id").fetchall()
    return render_template("users.html",users=rows)

@app.errorhandler(413)
def too_large(_):
    flash("File is too large. Maximum upload size is 10 MB.","error")
    return redirect(url_for("upload_material"))

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"),404

if __name__=="__main__":
    init_db()
    app.run(debug=True)
