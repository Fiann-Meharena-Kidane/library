import os

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
from wtforms import StringField, PasswordField, validators, SubmitField
from os import environ

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my-book-collection.db'
# connect app to our db,

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# silence error if set to False ?

db = SQLAlchemy(app)
# create a db object from SQLAlchemy class by passing our app,

Base = declarative_base()


class Book(Base, db.Model):
    # creates a Book table, inherits from both Base an db.Model too,

    __tablename__ = 'Books'
    # book name,

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    author = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    # columns of our table along with their constraints


if __name__ == '__main__':
    engine = create_engine('sqlite:///my-book-collection.db')
    Base.metadata.create_all(engine)

db.create_all()

all_books = []
# keeps track of dictionary of books added,


class ChangeRate(FlaskForm):
    # creates a from to change book rating,
    rate = StringField("New Rating", [validators.DataRequired()])
    submit = SubmitField("Change")
    # submit button


app.config['SECRET_KEY'] = "secret"  # secret key to protect from csrf attack,
bootstrap = Bootstrap(app)


@app.route('/', methods=['GET','POST'])
def authenticate():
    if request.method=='POST':
        admin_name=None
        admin_email=os.environ.get('EMAIL')
        admin_password=os.environ.get('PASS')

        name=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')

        if admin_password==password and admin_email==email:
            # if user is authenticated,
            return redirect(url_for('home'))
        else:
            return "Access Denied"
    else:
        # else if user not authenticated,
        return render_template('authenticate.html')


@app.route('/books', methods=['GET','POST'])
def home():
    # global Book
    all_rows = db.session.query(Book).all()
    # gets list of all books,

    return render_template('index.html', books=all_rows)
    # we pass the latest list of all books so that it renders them,


@app.route('/delete/<book_id>', methods=['POST', 'GET'])
def delete(book_id):

    db.session.delete(Book.query.get(book_id))
    db.session.commit()
    # when user deletes a book, get its id, then delete that book from our db using its id,

    return redirect(url_for('home'))
    # user redirected to home page, go to home function for more info,


@app.route("/add", methods=['POST', 'GET'])
def add():
    global Book
    global all_books
    if request.method == 'POST':
        # if user is submitting book details,
        # my_book = {
        #     "title": request.form['title'],
        #     "author": request.form['author'],
        #     "rating": request.form['rating']
        # }

        title = request.form['title']
        author = request.form['author']
        rating = request.form['rating']
        # gets data entered from user

        new_book = Book(title=title, author=author, rating=rating)
        db.session.add(new_book)
        db.session.commit()
        # and fill the next row in our table with this book,

        return redirect(url_for('home'))
        # user is directed to home page where all added books are rendered,

        # create dictionary and fill it with what user entered,
        # all_books.append(my_book)
        # update our all books list of dictionary,
        # print(all_books)

        # pass list of books to render it,
        # return f"{name},{author},{rating}"

    return render_template('add.html')
    # if form not validated, render add.html page so that user enters data again,


@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    form = ChangeRate()
    # create a form object,

    book = Book.query.filter_by(id=id).first()
    db.session.commit()
    # fetch the book user wants to alter its rating via its id,

    if form.validate_on_submit():
        new_rate = form.rate.data
        # if form is validated, hold the new rating value user entered

        Book.query.filter_by(id=id).first().rating = new_rate
        db.session.commit()
        # update our db by changing the rating  of this book ,

        all_rows = db.session.query(Book).all()
        # list of all book objects,


        return redirect(url_for('home', books=all_rows))
        # redirect to home,pass list of book objects so that homepage renders the updated list of books,

    return render_template('edit.html', book=book, form=form)
    # if form not validated, render edit.html page again, use form to get user data, and book to display book ..
    # .. name and current rating,


if __name__ == "__main__":
    app.run(debug=True)
