import json
import pandas




def compute_subtask_stats(input_folder, subtask):
    """
    compute:
    a. number of incidents per question
    b. number of gold docs per question
    c. number of questions

    :param str subtask: s1 | s2 | s3
    """


    answers = json.load(open(f'resources/{input_folder}/dev_data/s{subtask}/answers.json'))

    num_questions = len(answers)

    numerical_answers = [answer_info['numerical_answer']
                         for answer_info in answers.values()]

    avg_answer = sum(numerical_answers) / len(numerical_answers)

    num_gold_docs = []
    for q_id, answer_info in answers.items():

        all_gold_docs = []
        for inc_id, answer_docs in answer_info['answer_docs'].items():
            all_gold_docs.extend(answer_docs)

        num_gold_docs.append(len(all_gold_docs))

    avg_gold_docs = sum(num_gold_docs) / len(num_gold_docs)


    return (num_questions,
            round(avg_answer, 2),
            round(avg_gold_docs, 2))


list_of_lists = []

for label, input_folder in [('trial', 'trial_data_final'),
                            ('test', 'test_data_gold')]:
    for subtask in ['1',
                    '2',
                    '3']:
        num, avg_a, avg_d = compute_subtask_stats(input_folder, subtask)

        phase = ''
        if subtask == '1':
            phase = label

        one_row = [phase, subtask, num, avg_a, avg_d]

        list_of_lists.append(one_row)

stat_df = pandas.DataFrame(list_of_lists,
                           #columns=headers
                           )
latex_table = stat_df.to_latex(index=False, header=False)


row_one = ['', 'S', '\\#Qs', 'Avg ',        'Avg \\#']
row_two = ['', '',   '',     'Answer',      'gold docs']

header = ' & '.join(row_one) + '\\\\\n' + ' & '.join(row_two) + '\\\\\n'

latex_table = latex_table.replace('\\toprule', '\\toprule\n' + header)
print('\\begin{table}[H]')
print(latex_table)
print('\\caption{General statistics about trial and test data.}')
print('\\end{table}\n')