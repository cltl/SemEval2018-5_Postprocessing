import os
import json
import pandas
from collections import defaultdict
import seaborn as sns
import matplotlib.pylab as plt


def load_gold(gold_dir):
    """
    load gold data

    :param str gold_dir: path to gold data

    :rtype: dict
    :return: q_id -> gold numerical answer
    """
    q_id2answer = dict()

    for subtask in ['s2', 's3']:

        path_answers = os.path.join(gold_dir, 'dev_data', subtask, 'answers.json')
        assert os.path.exists(path_answers)

        subtask_answers = json.load(open(path_answers, 'rb'))
        num_qs = len(subtask_answers)

        sub_q_id2answer = dict()
        for q_id, answer_info in subtask_answers.items():
            sub_q_id2answer[q_id] = answer_info['numerical_answer']
        assert num_qs == len(sub_q_id2answer)

        q_id2answer.update(sub_q_id2answer)

    return q_id2answer


def load_systems(system_dir, gold, teams, max_value=-1, debug=0):
    """
    load system answers and score them using gold

    :param str system_dir: path to folder in which a folder is located for each system
    :param dict gold: see output load_gold function
    :param list teams: list of tuples (internal name, offical name)
    :param int max_value: every value >= max_value will be set to max_value
    this is to avoid the barplot from being to wide (1 to 171 for subtask 3)
    :param int debug: debug value

    :rtype: dict
    :return: class -> (system, subtask) -> [True -> answered and correct,
                               False -> answered and wrong,
                               None -> not answered and hence wrong]
    """
    class2subtask_system2answers = {}

    if debug:
        print()
        print('## debug info load_systems function')

    for subtask in ['2', '3']:

        for user, offical_name in teams:

            sys_path = f'{system_dir}/{user}/submitted/s{subtask}/answers.json'
            if not os.path.exists(sys_path):
                if debug:
                    print(f'no answers from {user} for {subtask}')

                continue

            system_answers = json.load(open(sys_path))

            for q_id, gold_answer in gold.items():

                if not q_id.startswith(subtask):
                    continue

                correct = None
                sys_answer = None
                if q_id in system_answers:
                    sys_answer = system_answers[q_id]['numerical_answer']
                    correct = sys_answer == gold_answer

                if debug >= 3:
                    print()
                    print(q_id)
                    print(gold_answer)
                    print(sys_answer)
                    print(correct)
                    input('continue?')

                if all([max_value,
                        gold_answer > max_value]):
                    gold_answer = max_value

                if gold_answer not in class2subtask_system2answers:
                    class2subtask_system2answers[gold_answer] = defaultdict(list)

                class2subtask_system2answers[gold_answer][(offical_name, subtask)].append(correct)

            if debug:
                print(f'answers for: subtask {subtask}, team {offical_name}')

    if debug:
        print()
        print('## end of debug info load_systems function')
        print()

    return class2subtask_system2answers


def load_viz_input(class2system_info, target_subtask, the_range=None, debug=0):
    """
    load input needed for vizualization

    :param dict class2system_info: see output load_systems
    :param str target_subtask: 2 | 3
    :param range the_range: range of gold class answers to be used
    :param int debug: debug value


    :rtype: tuple
    :return: (viz_df, list_of_perc_answered)
    """
    if debug:
        print()
        print('## debug info load_viz_input')

    list_of_lists = []
    headers = ['class', 'value', 'team']
    list_perc_answered = []

    for class_ in sorted(class2system_info):

        print(class_, the_range, class_ in the_range)
        if the_range:
            if class_ not in the_range:
                print(class_, 'not in range')
                continue

        for (team, subtask), team_info in sorted(class2system_info[class_].items()):

            if subtask != target_subtask:
                continue

            if debug >= 2:
                print()
                print(f'class {class_}, s{subtask}, team {team}, # {len(team_info)}')

            acc = 100 * (team_info.count(True) / len(team_info))
            not_answered = 100 * (team_info.count(None) / len(team_info))
            perc_answered = 100 - not_answered

            list_perc_answered.append(f'{round(perc_answered, 2)}%')

            if debug >= 2:
                print(f'class {class_}, team {team}, acc {acc}, perc {perc_answered}')

            one_row = [class_, acc, team]
            list_of_lists.append(one_row)

    viz_df = pandas.DataFrame(list_of_lists, columns=headers)

    if debug:
        print()
        print(viz_df.head())
        print('## end debug info load_viz_input')

    return viz_df, list_perc_answered


def create_barplot(viz_df, subtask, out_dir, list_percs=None):
    """
    create plot

    :param viz_df: see output load_viz_input
    :param str subtask: 2 | 3
    :param str out_dir: output directory for vizualizations
    :param list list_percs: list of perc answered for all members of a
    class for each system
    """
    ax = sns.barplot(x="class", y='value', hue="team", data=viz_df)
    sns.set_context(rc={"figure.figsize": (50, 25)})
    sns.set_style("white")

    for text_obj in ax.get_legend().get_texts():
        if text_obj._text == 'NewsReader':
            text_obj._text = '*NewsReader'

    ax.set_xticklabels(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10>'])

    plt.setp(ax.get_legend().get_texts(), fontsize='16')  # for legend text
    plt.setp(ax.get_legend().get_title(), fontsize='20')  # for legend title

    if list_percs:
        for counter, p in enumerate(ax.patches):
            height = p.get_height()
            perc_answered = list_percs[counter]
            ax.text(p.get_x() + p.get_width() / 2.,
                    height + 0.02,
                    perc_answered,
                    ha="center")

    ax.set_ylabel('Incident accuracy normalized')
    ax.set_xlabel('Gold answer class')
    the_title = f'Incident accuracy normalized for subtask {subtask} per gold answer class'
    ax.set_title(the_title)

    output_path = f'{out_dir}/s{subtask}.pdf'
    plt.savefig(output_path)


def create_barplot_v2(viz_df, subtask, out_dir, list_percs=None):
    """
    create plot

    :param viz_df: see output load_viz_input
    :param str subtask: 2 | 3
    :param str out_dir: output directory for vizualizations
    :param list list_percs: list of perc answered for all members of a
    class for each system
    """
    g = sns.FacetGrid(viz_df,
                      col="team",
                      col_order=['CarlaAbreu', 'ID-DE', 'NAI-SEA', '*NewsReader'],
                      margin_titles=False,
                      size=4,
                      aspect=.5)
    g.map(sns.barplot, "class", "value")
    sns.set_context(rc={"figure.figsize": (50, 25)})
    sns.set_style("white")


    # set xticklabels
    #g.set_xticklabels(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10>'])
    g.set_ylabels('Incident accuracy normalized')
    g.set_xlabels('numerical answer class')

    output_path = f'{out_dir}/s{subtask}.pdf'
    plt.savefig(output_path)
    plt.close()