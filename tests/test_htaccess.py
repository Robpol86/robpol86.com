"""Test .htaccess file."""

import time

import docker
import pytest
import requests


@pytest.fixture(autouse=True, scope='module')
def httpd():
    """Start a new detached httpd container, yield to the test, then stop the container."""
    client = docker.from_env()
    container = client.containers.run("httpd_alpine", detach=True, ports={'80/tcp': 8080})

    # Wait up to 10 seconds for httpd to finish starting.
    start_time = time.time()
    while time.time() - start_time <= 10:
        try:
            assert requests.head('http://localhost:8080').status_code == 200
        except (AssertionError, requests.exceptions.ConnectionError):
            time.sleep(0.1)
        else:
            break

    # Yield to caller, then stop.
    yield container
    container.stop()


def test_unaffected():
    """Make sure URLs not mentioned in the file work as expected."""
    assert requests.head('http://localhost:8080').status_code == 200
    assert requests.head('http://localhost:8080/index.html').status_code == 200
    assert requests.head('http://localhost:8080/sub/sub.html').status_code == 200

    assert requests.head('http://localhost:8080/sub/').status_code == 403


def test_404():
    """Test ErrorDocument 404."""
    response = requests.get('http://localhost:8080/dne.html')
    assert response.status_code == 404
    assert response.text == 'This is the 404 page.\n'

    assert requests.head('http://localhost:8080/sub/dne.html').status_code == 404


@pytest.mark.parametrize('path,location', [
    ('guides/Flashing-Motorola-Droid-to-Cricket', 'flash_droid_cricket.html'),
    ('guides/Flashing-Motorola-Droid-to-Cricket/', 'flash_droid_cricket.html'),
    ('guides/Wireless-Charging-Car-Dock', 'wireless_charging_car_dock.html'),
    ('image.php', 'photo_albums.html'),
    ('index.php/Atrix_Lapdock_Other_Uses', 'atrix_lapdock.html'),
    ('index.php/Flashing_Motorola_Droid_to_Cricket', 'flash_droid_cricket.html'),
    ('index.php/Lapdock_500_Teardown', 'atrix_lapdock.html'),
    ('index.php/US_RNS-510_Video_In_Motion', 'rns_510_vim.html'),
])
def test_rewrite_legacy(path, location):
    """Test RewriteRules for legacy URLs.

    :param str path: URL to query.
    :param str location: Expected redirected URL in response.
    """
    response = requests.head(f'http://localhost:8080/{path}')
    expected = f'https://robpol86.com/{location}'
    assert response.status_code == 301
    assert response.headers['Location'] == expected


@pytest.mark.parametrize('keyword,location', [
    ('jetta', 'vw_jsw_2010.html'),
    ('JETTA', 'vw_jsw_2010.html'),
    ('Motion', 'rns_510_vim.html'),
    ('workspaces', 'photo_albums.html'),
])
def test_rewrite_keywords(keyword, location):
    """Test RewriteRules for keywords.

    :param str keyword: Use in query URL.
    :param str location: Expected redirected URL in response.
    """
    expected = f'https://robpol86.com/{location}'
    for pre, post in (['', ''], ['one', 'two'], ['one/three', 'two/four.html']):
        response = requests.head(f'http://localhost:8080/{pre}{keyword}{post}')
        assert response.status_code == 301
        assert response.headers['Location'] == expected


@pytest.mark.parametrize('path,location', [
    ('imagecfg.html', ''),
    ('index.php/ImageCFG', 'imagecfg.html'),
    ('lapdock.html', ''),
    ('index.php/Atrix_Lapdock_Other_Uses', 'atrix_lapdock.html'),
    ('berto89.iso', ''),
    ('file.php/berto89_vim.iso', 'rns_510_vim.html'),
])
def test_rewrite_keywords_recursion(path, location):
    """Test RewriteRules for keywords without recursion.

    :param str path: URL to query.
    :param str location: Expected redirected URL in response.
    """
    if not location:
        # No redirect should happen.
        response = requests.head(f'http://localhost:8080/{path}')
        assert response.status_code == 200
        return

    expected = f'https://robpol86.com/{location}'
    for pre, post in (['', ''], ['one', 'two'], ['one/three', 'two/four.html']):
        for final_path in (getattr(f'{pre}{path}{post}', f)() for f in ('format', 'upper', 'lower')):
            response = requests.head(f'http://localhost:8080/{final_path}')
            assert response.status_code == 301
            assert response.headers['Location'] == expected


@pytest.mark.parametrize('path', ['index.php', 'menu.php'])
def test_rewrite_catch_alls(path):
    """Test catch all redirects.

    :param str path: URL to query.
    """
    response = requests.head(f'http://localhost:8080/{path}')
    assert response.status_code == 301
    assert response.headers['Location'] == 'https://robpol86.com/'
