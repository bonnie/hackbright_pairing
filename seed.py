"""adding existing pairing data to the site"""

from model import connect_to_db, db, Cohort, PeriodTimeSlot, PairingPeriod, \
                  Pairing, Student

def add_periods(cohort):
  """add pairing periods from a two csv files: slots and periods.

  cohort is an instance of the Cohort class. 

  sample slots.csv line:

  sample periods.csv line:

  """


def add_existing_pairs(cohort):
  """add existing pairs from csv file. 

  cohort is an instance of the Cohort class. 

  Example pairs.csv file line: 

  """


if __name__ == "__main__":

  from server import app
  connect_to_db(app)

  cohort_frodo_id = 'f16g'
  cohort = Cohort.query.filter_by(cohort_frodo_id=cohort_frodo_id)
  add_periods(cohort)
