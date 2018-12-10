# -*- coding: utf-8 -*-
"""The entrypoint for mecablr.
"""
from server import app


if __name__ == '__main__':
    app.run(threaded=True)
