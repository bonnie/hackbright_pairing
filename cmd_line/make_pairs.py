"""quick script to make pairs from existing pair list and levels"""

import random
from datetime import datetime

# global to track whether there's a solo pair yet
solo_pair = False

def find_pair(student, level):

  print "*******finding pair for", student

  global solo_pair

  possible_levels = [level, level + 1, level - 1, level + 2, level - 2]

  for pairing_level in possible_levels:
    print "trying level", pairing_level

    pairs_list = list(levels.get(pairing_level, set()))
    random.shuffle(pairs_list)

    for pair in pairs_list:
      if pair not in past_pairs[student]:
        levels[pairing_level].remove(pair)
        return ((student, level), (pair, pairing_level))

  # if we couldn't find anyone, try none

  if not solo_pair and '' not in past_pairs[student]:
    solo_pair = True
    return((student, level), (None, None))

  # we're up sh*t creek
  return None


# intialize students dict
past_pairs = {}

# for dealing with students in outer levels first
levels = {}

# there's a better way to do this...
for i in range(1, 11):
  levels[i] = set()

# get the levels
level_file = open('levels.csv')
for line in level_file:
  name, level = line.split(',')
  level = int(level)
  levels[level].add(name)

level_file.close()

# get the previous pairs
pairs_file = open('prev_pairs.csv')
for line in pairs_file:
  tokens = line.rstrip().split(',')

  name = tokens[0]
  past_pairs_set = set(tokens[1:])
  past_pairs[name] = past_pairs_set

pairs = set()

for i in range(1, 6):

  # pair the outer ranges first
  low_level = i
  high_level = 11 - i

  for level in [high_level, low_level]:
    while len(levels[level]) > 0:
      student = random.choice(list(levels[level]))
      levels[level].remove(student)
      pair = find_pair(student, level)
      pairs.add(pair)
      if not pair:
        print "couldn't find pair within two levels for", student, ". Giving up."
        exit()


# print the pairs
for p1, p2 in pairs:

  p1_name = p1[0]
  p2_name = p2[0]

  if p2_name == None:
    # add an empty string for none; only one addition necessary
    past_pairs[p1_name].add('')
  else:
    past_pairs[p1_name].add(p2_name)
    past_pairs[p2_name].add(p1_name)

  print p1_name, 'and', p2_name

# finally, make a new file with the new pairs
datestring = datetime.strftime(datetime.now(), '%Y%m%d')
outfile = open(datestring + '_prev_pairs.csv', 'w')

for student, pairs in past_pairs.items():
  line = ','.join([student] + list(pairs))
  outfile.write(line + '\n')