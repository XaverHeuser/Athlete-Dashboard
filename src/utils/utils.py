import os


def set_proxy():
    os.environ['http_proxy'] = 'http://sia-lb.telekom.de:8080'
    os.environ['https_proxy'] = 'http://sia-lb.telekom.de:8080'
