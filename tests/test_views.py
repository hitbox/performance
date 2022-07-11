def url_with_prefix(app, url):
    prefix = app.config['PREFIX']
    return prefix + url

def test_request_basic(app, client):
    response = client.get(url_with_prefix(app, '/'), follow_redirects=True)
    assert b'Performance' in response.data
