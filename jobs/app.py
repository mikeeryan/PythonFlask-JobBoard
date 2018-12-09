import sqlite3
from flask import Flask, render_template, g
# g is global helper - Global namespace to access the db

PATH = 'db/jobs.sqlite'  # own format file, mini-DB in one file

app = Flask(__name__)

def open_connection():
    # get the connection attribute from g obj
    connection = getattr(g, '_connection', None)  # if not found, return None
    if connection == None:
        # set both local var and g. attr to the connection
        connection = g._connection = sqlite3.connect(PATH)
    connection.row_factory = sqlite3.Row
    return connection

# fn to query the db - both for select and insert/update?
def execute_sql(sql, values=(), commit=False, single=False):
    connection = open_connection()
    # cursor is the imaginary worker bee
    cursor = connection.execute(sql, values)  # values for inserts?
    if commit == True:
        results = connection.commit()
    else:
        results = cursor.fetchone() if single else cursor.fetchall()
        # meaning return a single row?
    cursor.close()
    return results

# To ensure the close_connection function is called when the app_context
# is destroyed decorate it with:
@app.teardown_appcontext
def close_connection(exception):
    connection = getattr(g, '_connection', None)
    if connection is not None:
        connection.close()

@app.route('/')
@app.route('/jobs')
def jobs():
    jobs = execute_sql(
        'SELECT job.id, job.title, job.description
        , job.salary, employer.id as employer_id
        , employer.name as employer_name
        FROM job JOIN employer '
        ON employer.id = job.employer_id'
    )
    # now pass the results into the flask macro
    return render_template('index.html', jobs=jobs)