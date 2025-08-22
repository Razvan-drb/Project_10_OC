import json
from datetime import datetime

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

def is_future_competition(comp):
    comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
    return comp_date >= datetime.now()


def todatetime(value, fmt="%Y-%m-%d %H:%M:%S"):
    """Convert string to datetime object in Jinja templates."""
    return datetime.strptime(value, fmt)

def now():
    """Return current datetime for Jinja templates."""
    return datetime.now()

def get_club_by_name(name):
    return next((club for club in clubs if club['name'] == name), None)

def get_competition_by_name(name):
    return next((comp for comp in competitions if comp['name'] == name), None)

def is_future_competition(comp):
    comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
    return comp_date >= datetime.now()

app = Flask(__name__)
app.secret_key = 'something_special'

app.jinja_env.filters['todatetime'] = todatetime
app.jinja_env.globals['now'] = now

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



@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = get_competition_by_name(request.form['competition'])
    club = get_club_by_name(request.form['club'])
    places_required = int(request.form['places'])
    club_points = int(club['points'])

    if places_required <= 0:
        flash("Error: Must book at least 1 place")
        return render_template('welcome.html', club=club, competitions=competitions), 200

    # can not over spend club points
    # Test: test_overbooking_prevention()
    if places_required > club_points:
        flash(f"Error: Cannot book more than {club_points} points")
        return render_template('welcome.html', club=club, competitions=competitions), 200

    #  12 place booking limit
    # Test: test_booking_more_than_12_places_fails()
    if places_required > 12:
        flash("Error: Cannot book more than 12 places")
        return render_template('welcome.html', club=club, competitions=competitions), 200


    if places_required > int(competition['numberOfPlaces']):
        flash(f"Error: Cannot book more than {competition['numberOfPlaces']} places available")
        return render_template('welcome.html', club=club, competitions=competitions), 200

    # Successful booking
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - places_required

    # deduct points when places are booked
    # Test: test_points_deduction_after_booking()
    club['points'] = int(club['points']) - places_required
    save_clubs()
    save_competitions()
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# Public points board without authentication required
# Test: test_points_display()
@app.route('/points')
def pointsDisplay():
    club_email = request.args.get('from')
    club = get_club_by_email(club_email) if club_email else None
    return render_template('points.html',
                         club=club,
                         competitions=competitions if club else None,
                         clubs=clubs,
                         show_points=True)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
