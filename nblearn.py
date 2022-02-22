import json
import os
import string
import sys

stop_word = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
             'v', 'w', 'x', 'y', 'z', 'an', 'the','in', 'he', 'she', 'you', 'they', 'of',
             'for', 'we', 'some', 'my', 'and', 'on', '', 'which',
             'it', 'l', 'al', 'ed', 'im', 'by', '\n', '\t', 'your', 'yours', 'bf', 'our', 'at', 'us', 'to',
             'me', 'be', 'pm', 'his', 'her','ive', 'its', 'now', 'el', 'this', 'etc', 'him', 'ae', 'av',
            'that', 'their']
avoid_label_smoothing = ['p_label', 'n_label', 't_label', 'd_label', 'positive_count', 'negative_count',
                         'truthful_count', 'deceptive_count']
word_label_count = dict()


def get_all_files(input_path):
    folders = os.listdir(input_path)
    sub_folders = [os.path.join(input_path, folder) for folder in folders if os.path.isdir(os.path.join(input_path,
                                                                                                        folder))]
    files = []
    for positive_negative_folder in sub_folders:
        fold_folders = [os.path.join(positive_negative_folder, folder) for folder in
                        os.listdir(positive_negative_folder) if ('deceptive' in folder)
                        or ('truthful' in folder)]
        for fold_folder in fold_folders:
            for fold in os.listdir(fold_folder):
                fold = os.path.join(fold_folder, fold)
                if os.path.isdir(fold):
                    files1 = [os.path.join(fold, folder) for folder in os.listdir(fold) if '.txt' in folder]
                    files = files + files1
    return files


def get_label(filename):
    if ('positive' in filename) and ('truthful' in filename):
        return 'positive', 'truthful'
    elif ('positive' in filename) and ('deceptive' in filename):
        return 'positive', 'deceptive'
    elif ('negative' in filename) and ('truthful' in filename):
        return 'negative', 'truthful'
    return 'negative', 'deceptive'


def add_to_word_label_count(content, pn_label, td_label):
    content = content.translate(str.maketrans('', '', string.punctuation)).rstrip().lstrip().lower()
    word_break = content.split()
    default_count_dict = {'positive': 0, 'negative': 0, 'deceptive': 0, 'truthful': 0, 'num_doc': 0}
    check_present = dict()
    for each_word in word_break:
        if (each_word in stop_word) or (each_word[0].isdigit()) or (each_word[-1].isdigit()):
            continue
        label_count_dict = word_label_count.get(each_word, default_count_dict.copy())
        if check_present.get(each_word, 0) == 0:
            check_present[each_word] = 1
            label_count_dict['num_doc'] += 1
        label_count_dict[pn_label] = label_count_dict[pn_label] + 1
        label_count_dict[td_label] = label_count_dict[td_label] + 1
        word_label_count[each_word] = label_count_dict


def remove_low_frequency_words():
    keys = list(word_label_count.keys())
    for key in keys:
        if key in avoid_label_smoothing:
            continue
        if word_label_count[key]['num_doc'] <= 1:
            del word_label_count[key]


def smoothing_counting():
    positive_count = 0
    negative_count = 0
    truthful_count = 0
    deceptive_count = 0

    for key in word_label_count.keys():
        if key in avoid_label_smoothing:
            continue
        word_label_count[key]['positive'] += 1
        word_label_count[key]['negative'] += 1
        word_label_count[key]['truthful'] += 1
        word_label_count[key]['deceptive'] += 1
        positive_count += word_label_count[key]['positive']
        negative_count += word_label_count[key]['negative']
        truthful_count += word_label_count[key]['truthful']
        deceptive_count += word_label_count[key]['deceptive']

    word_label_count['positive_count'] = positive_count
    word_label_count['negative_count'] = negative_count
    word_label_count['truthful_count'] = truthful_count
    word_label_count['deceptive_count'] = deceptive_count


if __name__ == '__main__':
    input_path = sys.argv[1]
    files = get_all_files(input_path)
    p_label = 0
    n_label = 0
    t_label = 0
    d_label = 0
    for each_file in files:
        with open(each_file, 'r') as f:
            pn_label, td_label = get_label(each_file)
            if pn_label == 'positive':
                p_label += 1
            else:
                n_label += 1
            if td_label == 'truthful':
                t_label += 1
            else:
                d_label += 1
            add_to_word_label_count(f.read(), pn_label, td_label)
    word_label_count['p_label'] = p_label
    word_label_count['n_label'] = n_label
    word_label_count['t_label'] = t_label
    word_label_count['d_label'] = d_label
    remove_low_frequency_words()
    smoothing_counting()
    with open('nbmodel.txt', 'w') as parameter_file:
        parameter_file.write(json.dumps(word_label_count))