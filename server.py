"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Cohort, PeriodTimeSlot, PairingPeriod, \
                  Pairing, Student


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "delicious knishes"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/cohorts')
def list_cohorts():
    """List cohorts in the system"""

    cohorts = Cohort.query.all()
    return render_template("cohorts.html", cohorts=cohorts)

@app.route('/cohort/<frodo_cohort_id>')
def get_cohort_summary(frodo_cohort_id):
    """Get a summary for a particular cohort"""

    cohort_data = Cohort.query.filter_by(frodo_cohort_id=frodo_cohort_id).one()
    return render_template("cohort_summary.html", cohort_data=cohort_data)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5005)
