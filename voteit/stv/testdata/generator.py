from __future__ import unicode_literals

import json
from codecs import open
from random import shuffle, randint

VOTE_COUNT = 100
CANDIDATE_VOTES_MIN = 1
CANDIDATE_VOTES_MAX = 10
CANDIDATE_COUNT = 24
SEAT_COUNT = 15
SAMPLE_COUNT = 10

for sample in range(SAMPLE_COUNT):
    with open('names.txt', encoding='utf8') as infile:
        names = [line.strip() for line in infile.readlines() if len(line) > 2]
    shuffle(names)

    election = {
        'candidates': [names.pop() for i in range(CANDIDATE_COUNT)],
        'ballots': [],
        'seats': SEAT_COUNT,
    }

    for i in range(VOTE_COUNT):
        election['ballots'].append(list(set([election['candidates'][randint(0, CANDIDATE_COUNT-1)] for c in range(randint(CANDIDATE_VOTES_MIN, CANDIDATE_VOTES_MAX))])))

    output_filename = '{} in {} ({}).json'.format(CANDIDATE_COUNT, SEAT_COUNT, sample)
    with open(output_filename, 'w', encoding='utf8') as outfile:
        json.dump(election, outfile)
