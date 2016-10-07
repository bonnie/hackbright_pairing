"""functions to pull data from the frodo web site, using selenium"""

from selenium import webdriver
FELLOWSHIP_URL = "http://fellowship.hackbrightacademy.com/"
EXPLORER_URL = FELLOWSHIP_URL + "explorer/"

# to log into frodo and get info
import os
FRODO_PASSWORD = os.environ['FRODO_PASS']
FRODO_USERNAME = 'bonnie'

# queries
FRODO_ID_AND_LEVEL_QUERY_ID = '43'
STUDENT_DATA_QUERY_ID = '44'

# for exceptions
from selenium.common.exceptions import NoSuchElementException

# for dictionary -> request query string
from urllib import urlencode

# for parsing HTML
from bs4 import BeautifulSoup

def log_in(driver):
  """log in to frodo to access sensitive information"""

  driver.get(FELLOWSHIP_URL)

  try:
    userbox = driver.find_element_by_id('id_login')
    userbox.send_keys(FRODO_USERNAME)

    passbox = driver.find_element_by_id('id_password')
    passbox.send_keys(FRODO_PASSWORD)

    submit_button = driver.find_element_by_css_selector('button.primaryAction')
    submit_button.click()

    return True

  except NoSuchElementException:
    # no login info. Brand new browser instance, so there's no way we're
    # already logged in. Return False.
    return False

def get_sql_rows(driver, cohort_id, query_id, col_count):
  """return list rows of data as a list from the frodo SQL Explorer.

  Each row is represented as a sublist, with each column value as an item.
  """

  url_params = {'params': 'cohort_id:' + cohort_id}

  url = EXPLORER_URL + query_id + '?' + urlencode(url_params)
  driver.get(url)

  html_text = driver.page_source.encode("utf8", "ignore")
  soup = BeautifulSoup(html_text, 'html.parser')
  rows = soup.find_all('tr', { 'class': 'data-row'})

  # use beautiful soup to parse results out of the page -- classes are the 
  # column number in this instance
  query_data = []
  for row in rows: 
    rowdata = []
    for i in range(col_count):
      rowdata.append(row.find('td', {'class': str(i)}).get_text())
    query_data.append(rowdata)

  return query_data

def get_students(cohort_id):
  """get initial super data to load into pairings db"""

  # new driver for login and data extraction
  driver = webdriver.Firefox()
  
  student_data = {}

  if log_in(driver):
    # only collect data if login was possible

    rows = get_sql_rows(driver, cohort_id, STUDENT_DATA_QUERY_ID, col_count=5)

    for frodo_id, first_name, nickname, last_name, level in rows:
      if nickname:
        first_name = nickname

      fullname = ' '.join([first_name, last_name])
      student_data[frodo_id] = {'fullname': fullname, 'level': int(level)}

  driver.close()
  return student_data


def get_levels(cohort_id):
  """get student levels from frodo and return dict {frodo_id: level}

  example URL: 
  http://fellowship.hackbrightacademy.com/explorer/43/?params=cohort_id%3Af16g
  """

  # new driver for login and data extraction
  driver = webdriver.Firefox()
  
  student_levels = {}

  if log_in(driver):
    # only collect data if login was possible

    rows = get_sql_rows(driver, cohort_id, FRODO_ID_AND_LEVEL_QUERY_ID, col_count=2)

    for frodo_id, level in rows:
      student_levels[frodo_id] = int(level)

  driver.close()
  return student_levels


if __name__ == '__main__':

  # for testing
  cohort = 'f16g'
  print "*" * 8 + 'STUDENT DATA'
  print get_students(cohort)

  print 
  print "*" * 8 + 'LEVEL DATA'
  print get_levels(cohort)
