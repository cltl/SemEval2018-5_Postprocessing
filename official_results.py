import os
import utils
import subprocess
import sys

# input arguments
results_zip = '/Users/marten/Downloads/SemEval-2018 Task 5_ Counting Events and Participants in the Long Tail-17285-results.zip'
results_folder = 'results'
dir_path = os.path.dirname(os.path.realpath(__file__))
debug_value = 2

# remove results folder if it exists
utils.remove_folder(results_folder)

# unzip
team2folder = utils.unzip_it(results_zip, results_folder, debug=debug_value)

# move updated submission paramitamiza (with event coreference) to submissions
commands = ['cp resources/paramitamirza.txt results/submissions/paramitamirza/scores.txt',
            'cp resources/carlaabreu.txt results/submissions/CarlaAbreu/scores.txt'
            ]

for command in commands:
    try:
        output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(e)
        print('exiting script because there was an error copying updated scores.txt to submissions')
        sys.exit()


# load data
team2results = dict()
for team, folder in team2folder.items():

    if team == 'paramitamirza':
        continue

    path_scores_txt = os.path.join(folder, 'scores.txt')
    team_results = utils.load_results(path_scores_txt)
    team2results[team] = team_results

assert len(team2results) == 5

team2official_name = {
    '*Piek': '*NewsReader',
    'CarlaAbreu': 'CarlaAbreu',
    'superlyc': 'NAI-SEA',
    'baseline1': 'Baseline',
    'IDDE': 'IDDE'
}

# create official results
utils.create_official_results(team2results, team2official_name)


# TODO: coreference table

utils.create_overview_paper_results(team2results, team2official_name)




