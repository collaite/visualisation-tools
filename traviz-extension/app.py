"""
Copyright (2022) Kody Moodley

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
"""
import os
from os import listdir
from os.path import isfile, join
from unicodedata import name

from flask import Flask, render_template, request, jsonify
from flask_dropzone import Dropzone
import spacy
import requests
from nltk import sent_tokenize
import nltk
nltk.download('punkt')

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_TYPE='text',
    DROPZONE_DEFAULT_MESSAGE='Drop text witness files here or click to upload.',
    DROPZONE_MAX_FILE_SIZE=3,
    DROPZONE_MAX_FILES=10,
)

dropzone = Dropzone(app)


@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        file_path = os.path.join(app.config['UPLOADED_PATH'], f.filename)
        f.save(file_path)
        # You can return a JSON response then get it on client side:
        # (see template index.html for client implementation)
        # return jsonify(uploaded_path=file_path)

    return render_template('index.html')

@app.route('/compare_text_witnesses', methods=['POST', 'GET'])
def compare_text_witnesses():
    nlp = spacy.load("nl_core_news_lg")
    files_path = app.config['UPLOADED_PATH']
    onlyfiles = [f for f in listdir(files_path) if isfile(os.path.join(files_path, f))]

    witnesses = []
    current_file_nouns = []
    current_file_adjectives = []
    current_file_verbs = []
    current_file_adverbs = []

    for file in onlyfiles:
        if '.gitkeep' not in file and '.DS_Store' not in file:
            
            current_obj = {}
            current_obj['edition'] = str(file.replace(str(app.config['UPLOADED_PATH']), ''))
            current_file = open(os.path.join(files_path, file), 'r', encoding='utf-8')
            # sentences = sent_tokenize(current_file.read())
            current_obj['text'] = str(current_file.read())
            doc = nlp(current_obj['text'])
            current_obj['entities'] = []
            for ent in doc.ents:
                curr_ent = {}
                curr_ent['text'] = ent.text
                curr_ent['type'] = ent.label_
                current_obj['entities'].append(curr_ent)

            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN', 'PRON']):
                    current_file_nouns.append(token.text)
                elif (token.pos_ in ['VERB']):
                    current_file_verbs.append(token.text)
                elif (token.pos_ in ['ADV']):
                    current_file_adverbs.append(token.text)
                elif (token.pos_ in ['ADJ']):
                    current_file_adjectives.append(token.text)
            
                # print(token.text, token.pos_, token.dep_)
            
            current_obj['nouns'] = current_file_nouns
            current_obj['adjectives'] = current_file_adjectives
            current_obj['adverbs'] = current_file_adverbs
            current_obj['verbs'] = current_file_verbs



            witnesses.append(current_obj)
            # print()
            # print()
            # print(current_obj['edition'])
            # print()

    print("Got here! Kody")
    return render_template("results.html", data=witnesses)

if __name__ == '__main__':
    app.run(debug=True)
