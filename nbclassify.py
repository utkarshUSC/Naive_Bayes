import json
import math
import os
import string
import sys

stop_word = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
             'v', 'w', 'x', 'y', 'z', 'an', 'the', 'in', 'he', 'she', 'you', 'they', 'of', 'for', 'we', 'some', 'my',
             'and', 'on', '', 'which', 'it', 'l', 'al', 'ed', 'im', 'by', '\n', '\t', 'your', 'yours', 'bf', 'our',
             'at', 'us', 'to', 'me', 'be', 'pm', 'his', 'her', 'ive', 'its', 'now', 'el', 'this', 'etc', 'him', 'ae',
             'av', 'that', 'their', 'was', 'were', 'has', 'have', 'had', 'am', 'is', 'will', 'shall', 'would', 'should',
             'might', 'may', 'can', 'could']
word_label_count = dict()


def get_all_files(input_path):
    folders = os.listdir(input_path)
    sub_folders = [os.path.join(input_path, folder) for folder in folders if os.path.isdir(os.path.join(input_path,
                                                                                                        folder))]
    files = []
    for positive_negative_folder in sub_folders:
        fold_folders = [os.path.join(positive_negative_folder, folder) for folder in
                        os.listdir(positive_negative_folder) if os.path.isdir(os.path.join(positive_negative_folder,
                                                                                           folder))]
        for fold_folder in fold_folders:
            for fold in os.listdir(fold_folder):
                fold = os.path.join(fold_folder, fold)
                if os.path.isdir(fold):
                    files1 = [os.path.join(fold, folder) for folder in os.listdir(fold) if '.txt' in folder]
                    files = files + files1
    return files


def classify_label(content):
    p_label = word_label_count['p_label']
    n_label = word_label_count['n_label']
    d_label = word_label_count['d_label']
    t_label = word_label_count['t_label']
    total = p_label + n_label
    p = math.log(p_label / total)
    n = math.log(n_label / total)
    d = math.log(d_label / total)
    t = math.log(t_label / total)
    positive_count = word_label_count['positive_count']
    negative_count = word_label_count['negative_count']
    truthful_count = word_label_count['truthful_count']
    deceptive_count = word_label_count['deceptive_count']
    content = content.translate(str.maketrans('', '', string.punctuation)).rstrip().lstrip().lower()
    word_break = content.split()
    for each_word in word_break:
        each_word = each_word.strip()
        if each_word in stop_word:
            continue
        if word_label_count.get(each_word, "") != "":
            p_count = word_label_count[each_word].get('positive', 0)
            n_count = word_label_count[each_word].get('negative', 0)
            t_count = word_label_count[each_word].get('truthful', 0)
            d_count = word_label_count[each_word].get('deceptive', 0)
            if word_label_count[each_word].get('num_doc', 0) <= 1:
                continue
            p += math.log(p_count / positive_count)
            n += math.log(n_count / negative_count)
            t += math.log(t_count / truthful_count)
            d += math.log(d_count / deceptive_count)
    pn_label = 'positive'
    td_label = 'truthful'
    if p > n:
        pn_label = 'positive'
    else:
        pn_label = 'negative'

    if t > d:
        td_label = 'truthful'
    else:
        td_label = 'deceptive'

    return pn_label, td_label


if __name__ == '__main__':
    input_path = sys.argv[1]
    files = get_all_files(input_path)
    with open('nbmodel.txt', 'r') as parameter_file:
        word_label_count = json.load(parameter_file)
    with open('nboutput.txt', 'w') as write_file:
        for each_file in files:
            with open(each_file, 'r') as f:
                pn_label_predicted, td_label_predicted = classify_label(f.read())
                write_file.write(td_label_predicted + ' ' + pn_label_predicted + ' ' + each_file + '\n')
