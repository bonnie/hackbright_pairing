"""get ratings from hackbright web site"""

import requests
import os
from urllib import urlencode
import csv

FELLOWSHIP_URL = os.environ['FELLOWSHIP_URL']
EXPLORER_URL = FELLOWSHIP_URL + "explorer/"
LOGIN_URL = FELLOWSHIP_URL + "accounts/login/"

FRODO_PASSWORD = os.environ['FRODO_PASS']
FRODO_USERNAME = os.environ['FRODO_USER']

# queries
FRODO_ID_AND_LEVEL_QUERY_ID = '43'
STUDENT_DATA_QUERY_ID = '44'


def get_query_results(cohort_id, query_id):
    """ """

    # adapted this code from 
    # http://stackoverflow.com/questions/11892729/how-to-log-in-to-a-website-using-pythons-requests-module

    payload = {
        'login': FRODO_USERNAME,
        'password': FRODO_PASSWORD
    }

    # construct the query for the sql explorer
    url_params = {'params': 'cohort_id:' + cohort_id}
    params = '?' + urlencode(url_params)
    query_url = EXPLORER_URL + query_id 
    download_url = '/'.join([query_url, 'csv']) + params


    # Use 'with' to ensure the session context is closed after use.
    with requests.Session() as sess:

        # these lines influenced by http://stackoverflow.com/questions/13567507/passing-csrftoken-with-python-requests

        # gimme cookies
        sess.get(FELLOWSHIP_URL)
        csrftoken = sess.cookies['csrftoken']

        # login and password plus the necessary cookie
        payload = {
            'login': FRODO_USERNAME,
            'password': FRODO_PASSWORD,
            'csrfmiddlewaretoken': csrftoken
        }

        # in addition to the payload, set the referrer to login page, so that it accepts the cookies
        login_result = sess.post(LOGIN_URL, data=payload, headers={'Referer': FELLOWSHIP_URL})

        # get the csv results of the query
        csv_results = sess.get(download_url)

        # return a list of the data rows, first row is the "header"
        return csv_results.text.split('\r\n')


def get_students(cohort_id):
    """get initial super data to load into pairings db, return dict

    {frodo_id: 
        {'fullname': fullname, 
            'level': int(level)
        }
    }

    """

    rows = get_query_results(cohort_id, STUDENT_DATA_QUERY_ID)

    student_data = {}

    for row in rows[1:]: # skip header row

        if not row: 
        # skip empty rows
            continue

        frodo_id, first_name, nickname, last_name, level = row.split(',')

        if nickname:
            first_name = nickname

        fullname = ' '.join([first_name, last_name])
        student_data[frodo_id] = {'fullname': fullname, 'level': int(level)}

    return student_data


def get_levels(cohort_id):
  """get student levels from frodo and return dict {frodo_id: level}

  """

  rows = get_query_results(cohort_id, FRODO_ID_AND_LEVEL_QUERY_ID)

  student_levels = {}

  # skip header row
  for row in rows[1:]:
    if not row: 
      # skip empty rows
      continue


    frodo_id, level = row.split(',')
    student_levels[frodo_id] = int(level)

  return student_levels


if __name__ == '__main__':

  # for testing
  cohort = 'f17g'
  print "*" * 8 + 'STUDENT DATA'
  print get_students(cohort)

  print 
  print "*" * 8 + 'LEVEL DATA'
  print get_levels(cohort)
