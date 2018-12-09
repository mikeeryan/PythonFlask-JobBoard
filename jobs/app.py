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
    # do not split lines on the sql query
    jobs = execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id')
    # pass the results to the flask render_template method (Jinja2 engine)
    # .html must be in /templates
    return render_template('index.html', jobs=jobs)
    # in index.html the flask macro show_jobs(jobs) is called with my list jobs as the parameter

# fn to display a job - the "job" is a dict from which will pull data into other places
@app.route('/job/<job_id>')
def job(job_id):
    # but how is this job passed into the template? by query
    # also created a url in the show_job macro
    job = execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id WHERE job.id = ?'
                      ,[job_id], single=True)
    # where only 1 job will be returned - ? is a placeholder for id
    return render_template('job.html', job=job)

# for the employer_id found from the job dict/query
# run another query to pull full employer info
@app.route('/employer/<employer_id>')
def employer(employer_id):
    employer = execute_sql('SELECT * FROM employer WHERE id=?', [employer_id], single=True)
    jobs = execute_sql('SELECT job.id, job.title, job.description, job.salary FROM job JOIN employer ON employer.id = job.employer_id WHERE employer.id = ?', [employer_id])
    reviews = execute_sql('SELECT review, rating, title, date, status FROM review JOIN employer ON employer.id = review.employer_id WHERE employer.id = ?', [employer_id])
    return render_template('employer.html', employer=employer, jobs=jobs, reviews=reviews)