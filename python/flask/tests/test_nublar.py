import json

def get_flask_test_client():
    """ helper to get the flask test client """
    from nublar_example_python_flask import app
    return app.test_client()

def test_github_api_client():
    """ unit test for the github api class """
    from nublar_example_python_flask import github_jobs
    gh = github_jobs.API()
    python_jobs = gh.find_positions(description='python')
    assert len(python_jobs) > 0

def test_health():
    """ test the health endpoint """
    test_client = get_flask_test_client()
    response = test_client.get('/health', data=dict())
    data = json.loads(response.get_data(as_text=True))
    assert data['status'] == 'OK'

def test_python_jobs():
    """ test the page that shows python jobs """
    test_client = get_flask_test_client()
    response = test_client.get('/', data=dict())
    data = response.get_data(as_text=True)
    assert "id:" in data

def test_api_find_jobs():
    """ test the search endpoint """
    test_client = get_flask_test_client()
    response = test_client.get('api/find_jobs/python', data=dict())
    data = json.loads(response.get_data(as_text=True))
    assert len(data) > 0
