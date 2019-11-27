import json
import os


def data_extraction_library():
    with open('static/txt/library.txt', 'r') as f:
        doc = dict(eval((f.read())))

    dictwa = {}
    index = 0
    for title, author in doc.iteritems():
        dictwa.update({index: {"author": author, "title": title}})
        index += 1

    data = {"data": dictwa}

    with open('library.json', 'w') as writeit:
        json.dump(data, writeit)


def read_library():
    with open((str(os.path.dirname(os.path.abspath(__file__))) + '/static/json/library.json'), 'r') as f:
        jsonwa = f.read()
        f.close()

    return jsonwa
