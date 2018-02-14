import shutil
import os
import re
from glob import glob
import zipfile
import pandas
from operator import itemgetter


def p_r_f1(path, debug=False):
    """
    given path to output coreference, extract
    1. precision
    2. recall
    3. f1

    :param str path: path to output file *all.conll

    :rtype: tuple
    :return: (p, ,r, f1)
    """
    with open(path) as infile:
        raw = infile.read()
        regex = '[0-9]+.[0-9]+%'
        output = re.findall(regex, raw)

        if debug:
            print(path)
            print(raw)
            print(output)

        assert len(output) == 3

        r, p, f1 = output

        if debug:
            print(p, r, f1)

    return p, r, f1

if os.path.exists('results/submissions'):
    assert p_r_f1('results/submissions/Piek/s1/bcub_all.conll',
                  debug=False) == ('27.11%', '59.67%', '37.28%')
    assert p_r_f1('results/submissions/IDDE/s1/ceafe_all.conll',
           debug=False) == ('64.42%', '26.4%', '37.45%')
    assert p_r_f1('results/submissions/Piek/s1/bcub_all.conll',
                  debug=False) == ('27.11%', '59.67%', '37.28%')

def remove_folder(folder):
    """
    remove folder if it exists

    :param str folder: path to folder
    """
    if os.path.exists(folder):
        shutil.rmtree(folder)


def unzip_it(results_zip, results_folder, debug=False):
    """
    unzip results

    :param debug:
    :param str results_zip: path to download zip from codalab
    :param str results_folder: path to results folder

    :rtype: dict
    :return: team_name -> results folder for that team
    """
    teamname2folder = dict()

    with zipfile.ZipFile(results_zip, "r") as zip_ref:
        zip_ref.extractall(results_folder)

    submissions_dir = os.path.join(results_folder, 'submissions')
    os.mkdir(submissions_dir)

    for zip_folder in glob(results_folder + '/*output.zip'):

        basename = os.path.basename(zip_folder)

        team_name, dash, integer, *rest = basename.split()

        if debug:
            print()
            print(team_name, dash, integer)

        if all([team_name == 'paramitamirza',
                integer == '7']):
            team_name = 'IDDE'
            if debug:
                print('new team name', team_name)


        teamfolder = os.path.join(submissions_dir, team_name)
        with zipfile.ZipFile(zip_folder, "r") as zip_ref:
            zip_ref.extractall(teamfolder)

        teamname2folder[team_name] = teamfolder

        submitted_zip = zip_folder.replace('output', 'submission')
        assert os.path.exists(submitted_zip)
        submitted_out = os.path.join(teamfolder, 'submitted')

        with zipfile.ZipFile(submitted_zip, 'r') as zip_ref:
            zip_ref.extractall(submitted_out)

        if debug:
            print('unpacked to', teamfolder)

    return teamname2folder

def normalize(precision, perc_answered):
    """
    return normalized performance:
    precision / (100 / perc_answered)

    :param float precision: precision value on metric
    :param float perc_answered: percentage of question answered

    :rtype: float
    :return: precision / (100 / perc_answered)
    """
    if not perc_answered:
        return 0.0

    normalized = precision / (100 / perc_answered)

    return normalized


assert normalize(50, 50) == 25
assert normalize(0, 50) == 0
assert normalize(50, 0) == 0


def load_results(path_to_scores_txt):
    """

    :param str path_to_scores_txt: path to scores txt

    :rtype: dict
    :return: mapping metric to output value of system wrt that metric
    """
    metric2value = dict()

    with open(path_to_scores_txt) as infile:
        for line in infile:
            metric, value = line.strip().split(':')
            metric2value[metric] = float(value)

    assert len(metric2value) == 13, f'{metric2value} does not have need length of 13'

    return metric2value


def one_results_table(target_metric,
                      team2results,
                      team2official_name,
                      debug=0):
    """

    :param team2results:
    :param debug:
    :param target_metric:
    :return:
    """
    subtask = target_metric.split('_')[0]
    key_perc_answered = f'{subtask}_answered'

    list_of_lists = []
    header_perc_answered = f'{subtask} % answered'
    headers = ['team']

    if target_metric.endswith('coref_avg'):
        headers.append('men_coref_avg')
    else:
        headers.append(target_metric)
        headers.append(header_perc_answered)

    if any([target_metric.endswith('inc_accuracy'),
            target_metric.endswith('doc_f1')]):
        headers.insert(1, f'{target_metric} normalized')

    for team, results in team2results.items():

        team_result_for_metric = results[target_metric]
        perc_answered = results[key_perc_answered]

        if team_result_for_metric == 0:
            if debug >= 2:
                print(f'ignored {target_metric} for {team}: {team_result_for_metric}')
            continue

        assert type(team) == str
        assert type(team_result_for_metric) == float
        assert team_result_for_metric != 0
        assert type(perc_answered) == float

        # add asterix to piek because he is an organizer
        if team == 'Piek':
            team = '*Piek'


        one_row = [team2official_name[team], round(team_result_for_metric, 2)]

        if any([target_metric.endswith('inc_accuracy'),
                target_metric.endswith('doc_f1')]):
            normalized_score = normalize(team_result_for_metric, perc_answered)
            one_row.insert(1, round(normalized_score, 2))

        if not target_metric.endswith('coref_avg'):
            one_row.append(round(perc_answered, 2))

        list_of_lists.append(one_row)

    if not list_of_lists:
        if debug:
            print(f'no results for at all {target_metric}')
        return None


    if target_metric.endswith('rmse'):
        list_of_lists.sort(key=itemgetter(1), reverse=False)
        list_of_lists.sort(key=itemgetter(2), reverse=True)
    else:
        list_of_lists.sort(key=itemgetter(1), reverse=True)


    metric_result_df = pandas.DataFrame(list_of_lists, columns=headers)
    metric_result_df.index += 1
    return metric_result_df



def create_official_results(team2results, team2official_name):
    """
    create official results and write them to latex_input.txt

    :param team2results:
    :return:
    """
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
                result_df = one_results_table(target_metric,
                                                    team2results,
                                                    team2official_name,
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

def create_overview_paper_results(team2results, team2official_name):
    """
    create official results and write them to latex_input.txt

    :param team2results:
    :return:
    """
    # to dfs
    subtask_and_metrics = [('Incident-level evaluation', ['s2_inc_accuracy', 's2_inc_rmse',
                                                          's3_inc_accuracy', 's3_inc_rmse']),
                           ('Document-level evaluation', ['s1_doc_f1', 's2_doc_f1', 's3_doc_f1']),
                           ]

    caption_template = '\\caption{results for evaluation metric: \\textbf{%s}.}'

    with open('overview_paper.txt', 'w') as outfile:
        for subtask, target_metrics in subtask_and_metrics:

            outfile.write('\\subsection{%s}\n' % subtask)

            for target_metric in target_metrics:

                print(target_metric)
                result_df = one_results_table(target_metric,
                                              team2results,
                                              team2official_name,
                                              debug=0)

                if not target_metric.endswith('rmse'):
                    list_of_lists = []

                    short_metric_name = target_metric.replace('inc_accuracy', 'inc_acc')
                    headers = ['Team',
                               short_metric_name,
                               short_metric_name]

                    for index, row in result_df.iterrows():

                        norm = row[f'{target_metric} normalized']
                        precision = row[target_metric]

                        print(row)
                        print(subtask[1])
                        perc_answered = row[f's{target_metric[1]} % answered']
                        one_row = [row['team'],
                                   norm,
                                   f'{precision} ({perc_answered}%)']
                        list_of_lists.append(one_row)

                    result_df = pandas.DataFrame(list_of_lists, columns=headers)
                    result_df.index += 1

                latex_table = result_df.to_latex(column_format='cccc')

                if latex_table:
                    outfile.write('\\begin{table}[H]\n')
                    outfile.write('\\centering\n')
                    outfile.write('\\captionsetup{justification=centering}\n')
                    outfile.write('\\setlength\\tabcolsep{2pt}\n')

                    latex_table = latex_table.replace('{}', 'R')

                    if not target_metric.endswith('rmse'):

                        second_line = f'& & norm & (\% of Qs answered) \\\\ \n \\midrule \n'
                        latex_table = latex_table.replace('\\midrule', second_line)


                    outfile.write(latex_table)
                    outfile.write(caption_template % target_metric.replace('_', '\\_'))
                    outfile.write('\\end{table}\n')


    list_of_lists = []
    headers = ['Team']
    coref_metrics = [('bcub', 'BCUB'),
                     ('blanc', 'BLANC'),
                     ('ceafe', 'CEAF_E'),
                     ('ceafm', 'CEAF_M'),
                     ('muc', 'MUC')]

    headers.extend([item[1] for item in coref_metrics])
    headers.append('AVG')



    for user in ['IDDE', 'Piek', 'baseline1']:

        values = []

        if user == 'Piek':
            offical_name = '*NewsReader'
        else:
            offical_name = team2official_name[user]

        one_row = [offical_name]
        for coref_name, coref_table_name in coref_metrics:

            path = f'results/submissions/{user}/s1/{coref_name}_all.conll'
            assert os.path.exists(path), f'{path} does not exist'

            p, r, f1 = p_r_f1(path, debug=False)

            one_row.append(f1)

            values.append(float(f1[:-1]))

        # avg
        avg = float(team2results[user]['s1_men_coref_avg'])
        avg_string = f'{round(avg, 2)}%'
        one_row.append(avg_string)

        print()
        print('average according to filip', avg_string)
        print('average', avg)

        list_of_lists.append(one_row)

    coref_df = pandas.DataFrame(list_of_lists, columns=headers)
    coref_df.index += 1

    latex_table = coref_df.to_latex()
    latex_table = latex_table.replace('{}', 'R')


    with open('overview_paper.txt', 'a') as outfile:

        outfile.write('\\subsection{Event Coreference}\n')
        outfile.write('\\begin{table*}\n')
        outfile.write('\\centering\n')
        outfile.write('\\captionsetup{justification=centering}\n')

        outfile.write(latex_table)
        outfile.write('\\caption{Results for mention-level evaluation}.\n')
        outfile.write('\\end{table*}\n')


