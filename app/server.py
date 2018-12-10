# -*- coding: utf-8 -*-
"""Flask Application
"""
import json
from os import path
from typing import Optional
from flask import Flask, abort, request, Response


CONFIG_PATH = path.join(path.dirname(path.abspath(__file__)), 'flask.cfg')


app = Flask(__name__)
app.config.from_pyfile(CONFIG_PATH)

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
    if request.method == 'POST':
        data = request.data.decode('utf-8')
        data = json.loads(data)
        sentence = data.get('sentence')
    else:
        sentence = request.args.get('sentence')
    # STEP.2 Morphological Analysis
    if sentence is None:
        pass
    else:
        pass
    # STEP.3 Make a response object
    payload = json.dumps({'sentence': sentence}, ensure_ascii=False)
    res = {
        'response': payload,
        'status': 200,
        'content_type': 'application/json'
    }
    return Response(**res)
