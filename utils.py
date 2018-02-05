import shutil
import os
from glob import glob
import zipfile
import pandas
from operator import itemgetter


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


def one_results_table(target_metric, team2results, debug=0):
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


        one_row = [team, round(team_result_for_metric, 2)]

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
