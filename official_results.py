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
    path_scores_txt = os.path.join(folder, 'scores.txt')
    team_results = utils.load_results(path_scores_txt)
    team2results[team] = team_results

assert len(team2results) == 6


# to dfs
subtask_and_metrics = [('Subtask 1', ['s1_doc_f1']),
                       ('Subtask 2', ['s2_inc_accuracy', 's2_inc_rmse', 's2_doc_f1']),
                       ('Subtask 3', ['s3_inc_accuracy', 's3_inc_rmse', 's3_doc_f1']),
                       ('Event Coreference', ['s1_men_coref_avg'])
                      ]

caption_template = '\\caption{results for evaluation metric: \\textbf{%s}.\\hspace{\\textwidth} We mark explicitly with an asterisk the teams that had a task co-organizer as a team member}'

with open('latex_input.txt', 'w') as outfile:
    for subtask, target_metrics in subtask_and_metrics:

        outfile.write('\\section{%s}\n' % subtask)
        for target_metric in target_metrics:
            result_df = utils.one_results_table(target_metric,
                                                team2results,
                                                debug=0)
            latex_table = result_df.to_latex()
            if latex_table:
                outfile.write('\\begin{table}[H]\n')
                outfile.write('\\centering\n')
                outfile.write('\\captionsetup{justification=centering}')
                latex_table = latex_table.replace('{}', 'Rank')
                outfile.write(latex_table)

                metric_name = result_df.columns[1].replace('_', '\\_')
                metric_name = metric_name.replace(' normalized', '')
                outfile.write(caption_template % metric_name)
                outfile.write('\\end{table}\n')





