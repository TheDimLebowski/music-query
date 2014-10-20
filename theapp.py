# all the imports
import sqlite3
import pandas as pd
import json
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# configuration
DATABASE = 'releases.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/', methods = ['GET'])
def hello_world():
    return render_template('hello_world.html')

@app.route('/piechart', methods = ['GET'])
def piechart():
    year = request.args.get('year',2013)
    country = str(request.args.get('country','UK'))
    query = "select * from releases where country = '{0}' and year = {1} order by volume desc".format(country, year)
    cur = g.db.execute(query)
    entries = [[row[1], row[3]] for row in cur.fetchall()]
    return render_template('piechart.html',  year = year, country = country, entries = json.dumps(entries))

@app.route('/timeline', methods = ['GET'])
def timeline():
    country = str(request.args.get('country','UK'))
    query = "select * from releases where country = '{0}' order by volume desc".format(country)
    cur = g.db.execute(query)

    results_df = pd.DataFrame(cur.fetchall(), columns = ['year','genre','country','volume'])
    results_df = results_df.pivot(index = 'year', columns = 'genre', values = 'volume').reset_index()
    sorted_genres = results_df[list(set(results_df.columns) - set(['year']))].sum()
    sorted_genres.sort()
    sorted_genres = list(sorted_genres[::-1].index)
    results_df = results_df[['year']+sorted_genres]
    columns = results_df.columns.values
    values =  results_df.values


    names = [str(string) for string in results_df.columns.values]
    values =  results_df.values.tolist()

    return render_template('timeline.html', country = country, names = names, values = values )

if __name__ == '__main__':
    app.run()