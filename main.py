from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

app = Flask(__name__)

# Database
class Base(DeclarativeBase):
    pass

# Configures the SQlite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"

# Eextension
db = SQLAlchemy(model_class=Base)
# Initialise the app with the extension
db.init_app(app)

# Table
class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    # This will allow each book object to be identified by its title when printed
    def __repr__(self):
        return f"<Book {self.title}>"


# Table schema in the database. Requires application context
with app.app_context():
    db.create_all()

# Record
"""new_record = User(id='', title='', author='', rating=)
db.session.add(new_record)
db.session.commit()"""

@app.route("/")
def home():
    # Read all the records
    # A query to select from the database. 
    result = db.session.execute(db.select(Book).order_by(Book.title))
    # Scalars() - Gets the elements rather than entire rows from the database
    all_books = result.scalars()
    return render_template("index.html", books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # Create Record
        new_book = Book(
            title=request.form["title"],
            author=request.form["author"],
            rating=request.form["rating"],
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("home"))
    
    return render_template("add.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        # Update Record
        book_id = request.form["id"]
        # get_or_404, will return the book if the id matches or raise a 404 error if the object is not found
        book_to_update = db.get_or_404(Book, book_id)
        book_to_update.rating = request.form["rating"]
        db.session.commit()
        return redirect(url_for("home"))
    book_id = request.args.get("id")
    book_selected = db.get_or_404(Book, book_id)
    return render_template("edit_rating.html", book=book_selected)

@app.route("/delete")
def delete():
    book_id = request.args.get("id")

    # Delete the record by ID
    book_to_delete = db.get_or_404(Book, book_id)
    #book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)