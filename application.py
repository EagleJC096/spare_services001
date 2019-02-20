import os
import requests
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology

app = Flask(__name__)

api_key = "0RxgAUF1Du4vPT94lAmoSA"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return render_template("/index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()
    print(request.method)
    if request.method == "POST":
        print("inside POST")
        print(request.form)
        if not request.form.get("username"):
            print("inside IF")
            return "must provide username, 403"
        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password, 403"
        print("after IF")
        

        # Query database for username
        rows = db.execute("SELECT password, id FROM \"bookUser\" WHERE username = :username", {'username': request.form.get("username")}).fetchone()

        # Ensure username exists and password is correct
        if not rows or not check_password_hash(rows.password, request.form.get("password")):
            return "invalid username and/or password, 403"
        

        # Remember which user has logged in
        session["user_id"] = rows.id

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return "No username provided, 404"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password, 400"

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return "confirmation field empty, 400"

        elif request.form.get("password") != request.form.get("confirmation"):
            return "passwords don't match, 400"

        # Query database for username
        rows = db.execute("SELECT * FROM \"bookUser\" WHERE username = :username", {'username': request.form.get("username")}).fetchone()
        if rows:
            return "username already in use, 400"

        db.execute("INSERT INTO \"bookUser\" (\"username\", \"password\") VALUES (:username, :hash)", {'username': request.form.get("username"), 'hash': generate_password_hash(request.form.get("password"))})
        db.commit()

        rows = db.execute("SELECT id FROM \"bookUser\" WHERE username = :username", {'username': request.form.get("username")}).fetchone()
        session["user_id"] = rows.id
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        
        print(request.form.get("q"))
        q = request.form.get("q") + "%"
        q_two = "%" + request.form.get("q") + "%"
        isbns = db.execute("SELECT * FROM \"bookDB\" WHERE isbn LIKE :q", {'q': q})
        titles = db.execute("SELECT * FROM \"bookDB\" WHERE title LIKE :q", {'q': q_two})
        authors = db.execute("SELECT * FROM \"bookDB\" WHERE author LIKE :q", {'q': q_two})
        return render_template("results.html", search=request.form.get("q"), isbns=isbns, titles=titles, authors=authors)

    else:
        return redirect("/")

@app.route("/books/<book>")
def book(book):
    try:
        bookFetch = db.execute("SELECT * FROM \"bookDB\" WHERE isbn = :book", {'book': book}).fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": book})
    except Exception:
        return "invalid ISBN number, 404"

    print(res.json())
    resource = res.json()
    books = resource['books']
    print(books)
    for dic in books:
        print(dic)
        count = dic.get('work_ratings_count')
        reviews = dic.get('average_rating')
    title = bookFetch.title
    author = bookFetch.author
    year = bookFetch.year

    reviewFetch = db.execute("SELECT * FROM \"review\" WHERE isbn = :book", {'book': book}).fetchall()

    return render_template("book.html", isbn=book, title=title, author=author, year=year, reviewFetch=reviewFetch, total=count, avg=reviews)


@app.route("/submit_rev", methods=["POST"])
def submit_rev():
    isbn = request.form.get("isbn")
    print(request.form)
    stars = int(request.form.get("stars"))
    
    if stars < 1 or stars > 5:
        return "star number must be between 1 and 5, 403"
    
    if not request.form.get("title"):
        return "Must a give a title to review, 403"
    
    row = db.execute("SELECT \"username\" from \"bookUser\" WHERE id = :id", {'id': session["user_id"]}).fetchone()
    try:
        db.execute("INSERT INTO \"review\" (\"isbn\", \"stars\", \"username\", \"title\", \"text\") VALUES (:isbn, :stars, :username, :title, :text)", {'isbn': isbn, 'stars': stars, 'username': row.username, 'title': request.form.get("title"), 'text': request.form.get("text")})
        db.commit()
    except Exception:
        return "error, 404. Sorry, that is all we know."

    return redirect(f"/books/{isbn}")


@app.route("/api/<isbn>")
def api(isbn):
    try:
        bookFetch = db.execute("SELECT * FROM \"bookDB\" WHERE isbn = :book", {'book': isbn}).fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": isbn})
    except Exception:
        return "invalid ISBN number, 404"

    resource = res.json()
    books = resource['books']
    for dic in books:
        count = dic.get('work_ratings_count')
        reviews = dic.get('average_rating')

    dic = { "title": bookFetch.title,
            "author": bookFetch.author,
            "year": bookFetch.year,
            "isbn": isbn,
            "review_count": count,
            "average_score": reviews
    }

    return jsonify(dic)