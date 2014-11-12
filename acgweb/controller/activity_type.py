# coding: utf-8

from flask import render_template, json, flash, jsonify, abort, make_response
from acgweb import db
from acgweb.model.activity import Activity
from acgweb import config
from template_filter import *
from decorated_function import *

import jieba

activity_train_set = None


@app.route('/update_train_set')
@login_required
def update_train_set():
    non_word_list = ['', ' ', '\t', '(', ')', '【', '】', '（', '）', '-', ',', '.', ':', '，', '：', '；', '&', '\n', '\r', '\r\n']
    total = 0
    type_total = {}
    data_set = {}
    for type in range(len(CONST.activitytypename)):
        type_total[type] = 0
    activity_list = Activity.query.filter(Activity.type != CONST.ACTIVITY_UNKNOWN)
    for activity in activity_list:
        word_list = jieba.cut(activity.title.strip(), cut_all=True)
        type = activity.type
        for word in word_list:
            if not word in data_set:
                data_set[word] = {}
            if not type in data_set[word]:
                data_set[word][type] = 0
            data_set[word][type] += 1
            type_total[type] += 1
            total += 1

    fp = open(config.BASE_DIR + 'cache/train-set.txt', 'w')

    fp.write(str(total))
    for type in range(len(CONST.activitytypename)):
        fp.write("\t%s" % type_total[type])
    fp.write("\n")

    for word in data_set:
        if word in non_word_list:
            continue
        fp.write(word)
        for i in range(len(CONST.activitytypename)):
            if i not in data_set[word]:
                data_set[word][i] = 0
            fp.write("\t"+str(data_set[word][i]))
        fp.write("\n")
    fp.close()

    fp = open(config.BASE_DIR + 'cache/train-set-possibility.txt', 'w')

    fp.write("%f" % 1.0)
    for type in range(len(CONST.activitytypename)):
        fp.write("\t%f" % (type_total[type]*1.0 / total))
    fp.write("\n")

    for word in data_set:
        if word in non_word_list:
            continue
        fp.write(word)
        for i in range(len(CONST.activitytypename)):
            p = (data_set[word][i] + 1.0) / (type_total[i] + len(data_set))
            fp.write("\t%f" % p)
        fp.write("\n")
    fp.close()

    return redirect(url_for('manage'))


def activitytypeclassify(title):
    global activity_train_set
    if not activity_train_set:
        activity_train_set = {}
        fp = open(config.BASE_DIR + 'cache/train-set-possibility.txt', 'r')
        for line in fp:
            parts = line.strip().split("\t")
            if len(parts) > 1:
                word = unicode(parts[0])
                activity_train_set[word] = {}
                for i in range(1, len(parts)):
                    activity_train_set[word][i-1] = parts[i]
        fp.close()

    possibility = {}

    word_list = list(jieba.cut(title.strip(), cut_all=True))

    for type in range(len(CONST.activitytypename)):
        p = float(activity_train_set['1.000000'][type])
        for word in word_list:
            if word in activity_train_set:
                p *= float(activity_train_set[word][type])
        possibility[type] = p
    possibility_1 = sum(possibility.values())
    for i in possibility.keys():
        possibility[i] /= possibility_1
    max_possibility = max(possibility, key=possibility.get)
    if max_possibility < 0.5:
        max_possibility = 0
    return max_possibility


def test():
    count = 100
    correct = 0
    activity_list = Activity.query.limit(count)

    for activity in activity_list:
        classify = activitytypeclassify(activity.title)
        print activity.title, classify, activity.type
        if classify == activity.type:
            correct += 1

    print correct * 1.0 / count


@app.route('/classify_activity')
@login_required
def activityclassify():
    classify_activity()
    return redirect(url_for('activitymanage'))


def classify_activity():
    activity_list = Activity.query.filter(Activity.type == CONST.ACTIVITY_UNKNOWN)
    for activity in activity_list:
        type = activitytypeclassify(activity.title)
        activity.type = type
        print "%s\t%s" % (activity.title, type)
        #flash({'type': 'success', 'content': '%s : %s' % (activity.title, CONST.activitytypename[type])})
        db.session.add(activity)
        db.session.commit()

