"""make Hackbright pairs from existing pair list and levels"""

import random
from datetime import datetime
import glob

# files storing past pairs
FILENAME_SUFFIX = '_pastpairs.csv'
LEVELS_FILENAME = 'levels.csv'
TODAY_STRING = datetime.strftime(datetime.now(), '%Y%m%d')

def get_levels():
    """create and return a dict of student levels"""
    
    levels = {}
    students = set()

    # initialize levels dict
    for i in range(1, 11):
        levels[i] = []

    # get the levels
    level_file = open('levels.csv')
    for line in level_file:
        name, level = line.split(',')
        level = int(level)
        levels[level].append(name)
        students.add(name)

    level_file.close()
    return levels, students

def get_past_pairs(students):
    """create dict of past pairs from latest past pairs file"""

    past_pairs = {}

    previous_pairs_filename = get_latest_pairsfile()
    if not previous_pairs_filename:
        # there are no previous pairs
        return { student: [] for student in students } 

    pairs_file = open(previous_pairs_filename)
    for line in pairs_file:
        tokens = line.rstrip().split(',')

        name = tokens[0]
        past_pairs_list = tokens[1:]
        past_pairs[name] = past_pairs_list

    pairs_file.close()

    return past_pairs

def create_pairs(levels, past_pairs):
    """create a set of class pairs based on levels and past pairs"""

    # track whether there's a solo pair yet
    solo_pair = False

    pairs = set()

    # go through all the levels, from the outside in
    for i in range(1, 6):

      # pair the outer ranges first
      low_level = i
      high_level = 11 - i

      for level in [high_level, low_level]:

        # pick of students from this level one by one
        while len(levels[level]) > 0:
          student = random.choice(levels[level])
          levels[level].remove(student)
          solo_pair, pair = find_pair(student, level, past_pairs, levels, solo_pair)
          pairs.add(pair)

          # no suitable pair for this student. Abort!
          if not pair:
            print "couldn't find pair within two levels for", student, ". Giving up."
            exit()

    return pairs

def find_pair(student, level, past_pairs, levels, solo_pair):
    """the real work -- find pairs for a student based on level"""

    print "*******finding pair for", student

    possible_levels = [level, level + 1, level - 1, level + 2, level - 2]

    for pairing_level in possible_levels:
        print "trying level", pairing_level

        # get a random order of possible pairs
        pairs_list = levels.get(pairing_level, [])
        random.shuffle(pairs_list)

        for pair in pairs_list:
            if pair not in past_pairs[student]:

                # we have a winner! 
                levels[pairing_level].remove(pair)
                return solo_pair, ((student, level), (pair, pairing_level))

    # if we couldn't find anyone, try none
    if not solo_pair and '' not in past_pairs[student]:
        solo_pair = True
        return solo_pair, ((student, level), (None, None))

    # we're up sh*t creek
    return solo_pair, None


def get_latest_pairsfile():
    """return the pairs file in this directory with the latest date"""

    files = glob.glob('./*' + FILENAME_SUFFIX)

    if len(files) == 0:
        print "WARNING: No past pairs files found"
        return None

    # if there's a file from today from previous times running this script (and
    # not liking the results), don't include it
    todayfile_name = './' + TODAY_STRING + FILENAME_SUFFIX

    try:
        # this will throw exception if the file doesn't exist in the listing
        todayfile_index = files.index(todayfile_name)

        print "ignoring today's file: ", todayfile_name
        del files[todayfile_index]
    except:
        pass

    latest_file = sorted(files)[-1]
    print 'USING PAST PAIRS FILE', latest_file
    print

    return latest_file


def print_pairs(past_pairs, pairs):
    """print pairs and return new pairing info"""

    # print the pairs
    for p1, p2 in pairs:

        # format: p1, p2 = (student_name, student_level)

        p1_name = p1[0]
        p2_name = p2[0]

        if p2_name == None:
            # add an empty string for none; only one addition necessary
            past_pairs[p1_name].append('')
        else:
            past_pairs[p1_name].append(p2_name)
            past_pairs[p2_name].append(p1_name)

        print p1_name, 'and', p2_name

    return past_pairs


def update_pairsfile(past_pairs):
    """create a file incorporating new pairs information for next time"""

    # finally, make a new file with the new pairs
    datestring = TODAY_STRING
    outfile = open(datestring + FILENAME_SUFFIX, 'w')

    for student, pairs in past_pairs.items():
        line = ','.join([student] + pairs)
        outfile.write(line + '\n')

    # make dict of student levels
    levels, students = get_levels()


if __name__ == "__main__":

    # get the levels
    levels, students = get_levels()

    # get the previous pairs
    past_pairs = get_past_pairs(students)

    # keep iterating until the user says OK
    while True:

        # pair up the students
        pairs = create_pairs(levels, past_pairs)

        # give some output and record new pairings
        past_pairs = print_pairs(past_pairs, pairs)

        answer = raw_input("Do you accept these pairs? (y or n): ")

        if answer == 'y':
            # create new file for the past pairs
            update_pairsfile(past_pairs)
            break
