# -*- coding: utf-8 -*-
"""Flask Application
"""
import json
from os import path
from typing import Optional
from flask import Flask, abort, request, Response
import MeCab


CONFIG_PATH = path.join(path.dirname(path.abspath(__file__)), 'flask.cfg')
DIC_DIR = path.join('/', 'usr', 'local', 'lib', 'mecab', 'dic')


# Flask Application
app = Flask(__name__)
app.config.from_pyfile(CONFIG_PATH)

# MeCab
mecab = MeCab.Tagger(f"-d {path.join(DIC_DIR, 'mecab-ipadic-neologd')}")

@app.route('/', methods=['GET', 'POST'])
def parse():
    """Morphological Analysis by MeCab.

    Request Format:
        GET: /?sentence=アルミ缶の上にあるみかん
        POST: / -X "Content-Type: application/json"
            { "sentence": "アルミ缶の上にあるみかん" }
    """
    # STEP.1 Extraction of a given sentence
    sentence: Optional[str] = None
    try:
        if request.method == 'POST':
            sentence = request.json['sentence']
        else:
            sentence = request.args['sentence']
    except KeyError:
        abort(400, '`sentence` not found.')
    # STEP.2 Morphological Analysis
    result: Optional[str] = None
    if sentence is not None:
        parsed = mecab.parse(sentence)
        result = []
        for line in parsed.split('\n'):
            line = line.strip()
            elems = line.split('\t', 1)
            if line == 'EOS' or len(elems) <= 1:
                continue
            cols = ['Surface', 'PoS', 'PoS1', 'PoS2', 'PoS3',
                    'VerbConjugation', 'Original', 'Reading', 'Pronunciation']
            result.append(dict(zip(cols, [elems[0]] + elems[1].split(','))))
    # STEP.3 Make a response object
    payload = json.dumps({'sentence': sentence, 'result': result}, ensure_ascii=False)
    res = {
        'response': payload,
        'status': 200,
        'content_type': 'application/json'
    }
    return Response(**res)
