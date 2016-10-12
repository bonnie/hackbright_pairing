"""Models and database functions for Pairings project.

Skeleton from Hackbright Ratings exercise."""

from flask_sqlalchemy import SQLAlchemy
from frodo_scraper import get_levels, get_students

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

##############################################################################
# Model definitions

class Cohort(db.Model):
    """Cohort containing students to be paired."""

    __tablename__ = "cohorts"

    cohort_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    frodo_cohort_id = db.Column(db.String(8), nullable=False) # cohort ID from frodo; example: f16g
    cohort_name = db.Column(db.String(64), nullable=False) # cohort name; example "Fall 16 Grace"

    def __repr__(self):
      """Provide helpful representation when printed."""

      repr_string = "<Cohort cohort_id={} frodo_cohort_id={}, cohort_name={}>"
      return repr_string.format(self.cohort_id, 
                                self.frodo_cohort_id,
                                self.cohort_name)

    def add_students(self):
      """add students from frodo web site for this cohort"""

      # students will be a dictionary, with keys as frodo_ids, values as dicts
      students = get_students(self.frodo_cohort_id)

      for frodo_id, data in students.items():
        jessica = Student(student_frodo_id=frodo_id,
                          full_name=data['fullname'],
                          current_rating=data['level'],
                          cohort_id=self.cohort_id)
        db.session.add(jessica)

      db.session.commit()

    def update_ratings(self):
      """use info from frodo to update ratings for students"""

      ratings = get_levels(self.frodo_cohort_id)

    def check_pair(self, student1_id, student2_id):
      """return pairing period for which this pair exists, None if the pair doesn't exist"""

      id1, id2 = sorted(student1_id, student2_id)

      pair_query = Pairing.query(pairing_id)
      pair_query = pair_query.filter_by(cohort_id=self.cohort_id, 
                                        student_id1=id1, 
                                        student_id2=id2)

      try:
        pair_count = pair_query.one()
        return pair_count.period

      except NoResultFound:
        return None


class PeriodTimeSlot(db.Model):
  """lab period time slot"""

  __tablename__ = "timeslots"

  timeslot_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  timeslot_date = db.Column(db.DateTime)
  timeslot_period = db.Column(db.String(16)) # this will be Morning or Evening

  def __repr__(self):
      """Provide helpful representation when printed."""

      repr_string = "<PeriodTimeSlot timeslot_id={} timeslot_date={} timeslot_period={}>"
      return repr_string.format(self.timeslot_id, 
                                strftime(self.timeslot_date, '%Y-%m-%d'),
                                self.timeslot_period)

class PairingPeriod(db.Model):
  """period for which students need to be paired"""

  __tablename__ = "pairingperiods"

  period_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  cohort_id = db.Column(db.ForeignKey("cohorts.cohort_id"))
  period_name = db.Column(db.String(256), nullable=False)
  period_start = db.Column(db.ForeignKey("timeslots.timeslot_id"))
  period_end = db.Column(db.ForeignKey("timeslots.timeslot_id"))

  cohort = db.relationship("Cohort",
                           backref=db.backref("pairing_periods")) 
                           # can't order by here, because date is in timeslot table...

  def __repr__(self):
      """Provide helpful representation when printed."""

      repr_string = "<PairingPeriod period_id={} period_name={}>"
      return repr_string.format(self.period_id, 
                                self.period_name)


  def add_pair(self, student1_id, student2_id):
    """add a pair for this period"""

    id1, id2 = sorted(student1_id, student2_id)

    pair = Pairing(pairing_period=self.period_id, student1_id=id1, student2_id=id2)
    db.session.add(pair)
    db.session.commit()


class Pairing(db.Model):
  """actual instance of a pairing"""

  __tablename__ = "pairings"

  pairing_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  pairing_period = db.Column(db.ForeignKey("pairingperiods.period_id"))

  # for consistency, student1_id < student2_id
  student1_id = db.Column(db.ForeignKey("students.student_id"))
  student2_id = db.Column(db.ForeignKey("students.student_id"))

  period = db.relationship("PairingPeriod",
                           backref=db.backref("pairings"))


  def __repr__(self):
    """Provide helpful representation when printed."""

    repr_string = "<Pairing pairing_id={} student1_id={}, student2_id={}>"
    return repr_string.format(self.student_id, 
                              self.full_name,
                              self.cohort_name)


class Student(db.Model):
  """student to be paired"""

  __tablename__ = "students"

  student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  student_frodo_id = db.Column(db.Integer)
  full_name = db.Column(db.String(512), nullable=False)
  current_rating = db.Column(db.Integer)
  cohort_id = db.Column(db.Integer, db.ForeignKey("cohorts.cohort_id"))

  cohort = db.relationship("Cohort", 
                           backref=db.backref("students", order_by=current_rating))

  def __repr__(self):
    """Provide helpful representation when printed."""

    repr_string = "<Student student_id={} full_name={}, current_rating={}>"
    return repr_string.format(self.student_id, 
                              self.full_name,
                              self.current_rating)

  def get_pairings(self):
    """return a dict of pairings for this student"""

    # necessary? 

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pairings'
#    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    # db.drop_all()
    # db.create_all()
    # f16g = Cohort(frodo_cohort_id='f16g', cohort_name='Fall 2016 Grace')
    # db.session.add(f16g)
    # db.session.commit()
    # f16g.add_students()
    print "Connected to DB."
