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

def is_future_competition(comp):
    comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
    return comp_date >= datetime.now()


#  trouver des clubs et des competitions. reduire le nombre try / except dans le code.
def get_club_by_email(email):
    return next((club for club in clubs if club['email'] == email), None)



app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip()
    if not email:
        flash("Please enter an email address")
        return redirect(url_for('index'))

    club = get_club_by_email(email)

    # do not crash when unknown email entered
    # Test: test_unknown_email_shows_error()
    if not club:
        flash("Error: Email not found. Please try again.")
        return redirect(url_for('index'))


    future_comps = [c for c in competitions if is_future_competition(c)]

    return render_template('welcome.html', club=club, competitions=future_comps)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


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

if __name__ == '__main__':
    app.run(debug=True)