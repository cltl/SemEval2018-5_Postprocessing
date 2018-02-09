import os
import subprocess
import sys
import utils
import vizualization_utils as viz_utils

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
            'cp resources/carlaabreu.txt results/submissions/CarlaAbreu/scores.txt',
            'cp resources/carlaabreu_s3_answers.json results/submissions/CarlaAbreu/submitted/s3/answers.json',
            'scp -r $lod:/home/filten/LongTailQATask/Evaluation/package_test_data/test_data_gold resources'
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

# create overview paper results
utils.create_overview_paper_results(team2results, team2official_name)

# vizualization
answers = viz_utils.load_gold('resources/test_data_gold/')
teams = [
    ('Piek', 'NewsReader'),
    ('CarlaAbreu', 'CarlaAbreu'),
    ('superlyc', 'NAI-SEA'),
    ('baseline1', 'Baseline'),
    ('IDDE', 'IDDE')
]
debug_value = 1
output_dir = 'output'

for subtask in ['2', '3']:
    class2subtask_system2answers = viz_utils.load_systems('results/submissions/',
                                                          answers,
                                                          teams,
                                                          max_value=10,
                                                          debug=1)

    viz_df, list_percs = viz_utils.load_viz_input(class2subtask_system2answers,
                                                  subtask,
                                                  the_range=range(0, 1000),
                                                  debug=debug_value)

    output = viz_utils.create_barplot(viz_df, subtask, output_dir)

