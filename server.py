import json
from datetime import datetime

from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

def get_club_by_name(name):
    return next((club for club in clubs if club['name'] == name), None)

def get_competition_by_name(name):
    return next((comp for comp in competitions if comp['name'] == name), None)

def is_future_competition(comp):
    comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
    return comp_date >= datetime.now()

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    comp = get_competition_by_name(competition)
    club_data = get_club_by_name(club)

    if not comp or not club_data:
        flash("Error: Competition or club not found")
        return redirect(url_for('index'))

    # can not book past competitions
    # Test: test_book_with_past_competition()
    if not is_future_competition(comp):
        flash("Error: Cannot book places for past competitions")
        return redirect(url_for('showSummary'))

    return render_template('booking.html', club=club_data, competition=comp)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))