import json
from flask import Flask,render_template,request,redirect,flash,url_for
import os


def loadClubs():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, 'clubs.json')) as c:
        return json.load(c)['clubs']

def loadCompetitions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, 'competitions.json')) as comps:
        return json.load(comps)['competitions']

def save_clubs():
    with open('clubs.json', 'w') as f:
        json.dump({'clubs': clubs}, f)

def save_competitions():
    with open('competitions.json', 'w') as f:
        json.dump({'competitions': competitions}, f)

#  trouver des clubs et des competitions. reduire le nombre try / except dans le code.
def get_club_by_email(email):
    return next((club for club in clubs if club['email'] == email), None)

def get_club_by_name(name):
    return next((club for club in clubs if club['name'] == name), None)

def get_competition_by_name(name):
    return next((comp for comp in competitions if comp['name'] == name), None)


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
    if not club:
        flash("Error: Email not found. Please try again.")
        return redirect(url_for('index'))

    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = get_competition_by_name(request.form['competition'])
    club = get_club_by_name(request.form['club'])
    places_required = int(request.form['places'])

    if places_required <= 0:
        flash("Error: Must book at least 1 place")
        return render_template('welcome.html', club=club, competitions=competitions), 200

    if places_required > int(club['points']):
        flash(f"Error: Cannot book more than {club['points']} points")
        return render_template('welcome.html', club=club, competitions=competitions), 200

    # Successful booking
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - places_required
    club['points'] = int(club['points']) - places_required
    save_clubs()
    save_competitions()
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display
@app.route('/points')
def pointsDisplay():
    club_email = request.args.get('from')
    club = get_club_by_email(club_email) if club_email else None
    return render_template('welcome.html',
                         club=club,
                         competitions=competitions if club else None,
                         clubs=clubs,
                         show_points=True)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)