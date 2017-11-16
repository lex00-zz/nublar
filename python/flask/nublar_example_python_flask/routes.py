from . import app
from flask import render_template
import json

@app.route("/")
def python_jobs():
    from .github_jobs import API as gh
    github = gh()
    python_jobs = github.find_positions(description='python')
    return render_template('python_jobs.html', python_jobs=python_jobs)

@app.route("/health")
def health():
    health = {'status': 'OK'}
    return json.dumps(health)
