from . import app
from flask import render_template
import json

@app.route("/health")
def health():
    """ health endpoint for monitoring """
    health = {'status': 'OK'}
    return json.dumps(health)

@app.route("/")
def python_jobs():
    """
    Lookup all python jobs and render them to a template
    """
    from .github_jobs import API as gh
    github = gh()
    python_jobs = github.find_positions(description='python')
    return render_template('python_jobs.html', python_jobs=python_jobs)

@app.route("/api/find_jobs/<description>")
@app.route("/api/find_jobs/<description>/<location>")
def find_jobs(description=None, location=''):
    """ Return the raw GitHub API response """
    from .github_jobs import API as gh
    github = gh()
    jobs = github.find_positions(description=description, location=location)
    return json.dumps(jobs)
