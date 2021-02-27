from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class RatingForm(FlaskForm):
    rating = StringField("Your rating out of 10", validators=[DataRequired()])
    review = StringField("Your review", validators=[DataRequired()])
    submit = SubmitField("Submit")


class MovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=True)
    year = db.Column(db.String(250), nullable=True)
    description = db.Column(db.String(1000), nullable=True)
    rating = db.Column(db.String(250), nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)


db.create_all()


@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(movies)):
        movies[i].ranking = len(movies)-i
    db.session.commit()
    return render_template("index.html", movies=movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RatingForm()
    id = request.args.get('id')
    movie_selected = Movie.query.get(id)
    if form.validate_on_submit():
        movie_selected.rating = float(request.form['rating'])
        db.session.commit()
        movie_selected.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form)


@app.route("/delete")
def delete():
    id = request.args.get('id')
    movie_selected = Movie.query.get(id)
    db.session.delete(movie_selected)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = MovieForm()
    if form.validate_on_submit:

        if request.method == "POST":
            params = {
                "api_key": "a92f8738c2db8608939bfd4b6704a4c5",
                "query": request.form["title"]
            }

            response = requests.get(
                "https://api.themoviedb.org/3/search/movie", params=params)
            data = response.json()
            movies_list = []
            for i in range(len(data["results"])):
                movie_dict = {
                    "title": data["results"][i]["original_title"],
                    "release": data["results"][i]["release_date"],
                    "id": data["results"][i]["id"]
                }
                movies_list.append(movie_dict)

            return render_template("select.html", movie_list=movies_list)
    return render_template("add.html", form=form)


@app.route("/get-details")
def GetDetails():
    movie_id = request.args.get("id")
    if movie_id:
        parameters = {
            "api_key": "a92f8738c2db8608939bfd4b6704a4c5"
        }
        res = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}", params=parameters)

        data_movies = res.json()

        new_movie = Movie(
            title=data_movies["original_title"],
            year=data_movies["release_date"].split("-")[0],
            description=data_movies["overview"],
            img_url=f"https://image.tmdb.org/t/p/w500{data_movies['poster_path']}"
        )
        db.session.add(new_movie)
        db.session.commit()

        m_id = new_movie.id
        return redirect(url_for('edit', id=m_id))


if __name__ == '__main__':
    app.run(debug=True)
