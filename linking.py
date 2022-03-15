import os
import csv
import json


dicts_path = {
    'biology': 'dicts/biology.txt',
    'chemistry': 'dicts/chemistry.txt',
    'chinese': 'dicts/chinese.txt',
    'english': 'dicts/english.txt',
    'geo': 'dicts/geo.txt',
    'history': 'dicts/history.txt',
    'math': 'dicts/math.txt',
    'physics': 'dicts/physics.txt',
    'politics': 'dicts/politics.txt'
}

csv_path = {
    'biology': 'processed_3.0/biology_concept_entities.csv',
    'chemistry': 'processed_3.0/chemistry_concept_entities.csv',
    'chinese': 'processed_3.0/chinese_concept_entities.csv',
    'geo': 'processed_3.0/geo_concept_entities.csv',
    'history': 'processed_3.0/history_concept_entities.csv',
    'math': 'processed_3.0/math_concept_entities.csv',
    'physics': 'processed_3.0/physics_concept_entities.csv',
    'politics': 'processed_3.0/politics_concept_entities.csv'
}

entity_dict = {}
for subject in csv_path.keys():
    entity_list = {}
    csv_file = open(csv_path[subject], 'r', encoding='utf-8-sig')
    csv_iter = csv.reader(csv_file)
    first_row = True
    label_col = -1
    uri_col = -1
    for row in csv_iter:
        if first_row:
            for i in range(len(row)):
                if row[i] == 'label':
                    label_col = i
                elif row[i] == 'uri':
                    uri_col = i
            first_row = False
        else:
            entity_list[row[label_col]] = row[uri_col]
    entity_dict[subject] = entity_list
    csv_file.close()


def csv2dict(csv_path: str, dict_path: str) -> None:
    f_csv = open(csv_path, 'r')
    f_dict = open(dict_path, 'w')
    csv_iter = csv.reader(f_csv)
    first_row = True
    label_col = -1
    for row in csv_iter:
        if first_row:
            for i in range(len(row)):
                if row[i] == 'label':
                    label_col = i
                    break
            first_row = False
            continue
        else:
            f_dict.write('%s 1\n' % row[label_col].strip('\"'))
    f_csv.close()
    f_dict.close()


def gen_dict(prefix):
    csv_prefix = 'processed_3.0'
    for name in os.listdir(csv_prefix):
        if name == '.DS_Store':
            continue
        csv2dict('%s/%s' % (csv_prefix, name), '%s/%s.txt' % (prefix, name.split('_')[0]))


def process(content, subject):
    # if subject == 'english':
    #     return None
    import jieba
    jieba.load_userdict(dicts_path[subject])
    words = jieba.lcut(content)
    del jieba
    cursor = 0
    label_map = {}
    for word in words:
        if word in entity_dict[subject].keys():
            if word in label_map.keys():
                label_map[word]['where'].append([cursor, cursor + len(word)])
            else:
                label_map[word] = {
                    'uri': entity_dict[subject][word],
                    'where': [[cursor, cursor + len(word)]]
                }
        cursor += len(word)
    data = []
    for label in label_map.keys():
        data.append({
            'label': label,
            'uri': label_map[label]['uri'],
            'where': label_map[label]['where']
        })
    # if data == []:
    #    return None
    return data


def process_json(json_path):
    json_file = open(json_path, 'r')
    content = json.load(json_file)
    json_file.close()
    subject = content['Subject']
    if subject == 'english':
        return None
    text = ''
    if content['Content'] is not None and content['Content'] != '':
        text = text + '\n' + content['Content']
    for question in content['Questions']:
        if question['Question'] is not None and question['Question'] != '':
            text = text + '\n' + question['Question']
        if question['QuestionType'] == 'choosing' and question['Choices'] is not None:
            for choice in question['Choices']:
                text = text + '\n' + choice
        elif question['QuestionType'] != 'answering-essay':
            assert question['Answer'] is not None
            text = text + '\n' + question['Answer']

    return process(text, subject)


if __name__ == '__main__':
    # gen_dict('dicts')
    json_root = '/Users/flagerlee/GaoKao_generate/json'
    path_prefix = 'temp'
    if not os.path.exists(path_prefix):
        os.mkdir(path_prefix)
    for year_name in os.listdir(json_root):
        if year_name == '.DS_Store':
            continue
        if not os.path.exists('%s/%s' % (path_prefix, year_name)):
            os.mkdir('%s/%s' % (path_prefix, year_name))
        for exam_id in os.listdir('%s/%s' % (json_root, year_name)):
            if exam_id == '.DS_Store':
                continue
            if not os.path.exists('%s/%s/%s' % (path_prefix, year_name, exam_id)):
                os.mkdir('%s/%s/%s' % (path_prefix, year_name, exam_id))
            for problem_json in os.listdir('%s/%s/%s' % (json_root, year_name, exam_id)):
                if problem_json == '.DS_Store':
                    continue
                suffix = '%s/%s/%s' % (year_name, exam_id, problem_json)
                res = process_json('%s/%s' % (json_root, suffix))
                if res is not None:
                    with open('%s/%s/%s/%s' % (path_prefix, year_name, exam_id, problem_json.split('.')[0] + '.txt'), 'w') as f2:
                        f2.write(str(res))