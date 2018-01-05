#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask
import config
from werkzeug.contrib.cache import SimpleCache

application = Flask(__name__)
application.config.from_object("config")
cache = SimpleCache()

from myapp import views
from myapp import admin_views