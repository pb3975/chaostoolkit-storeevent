# -*- coding: utf-8 -*-
# a chaosdb control class to write events directly into grafana data store as
# annotations using the annotations HTTP API

import requests
import json
from requests.auth import HTTPBasicAuth
import time
from logzero import logger
from chaoslib.types import Configuration, Secrets

import logging

# Enabling debugging at http.client level (requests->urllib3->http.client)
# you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# the only thing missing will be the response.body which is not logged.
try: # for Python 3
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
HTTPConnection.debuglevel = 1

logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

__all__ = [
    "cleanup_control",
    "configure_control",
    "before_experiment_control",
    "after_experiment_control",
    "before_method_control",
    "after_method_control",
    "before_activity_control",
    "after_activity_control",
    "post_event"
]

# global defaults

def cleanup_control():
    return 1


def configure_control(c: Configuration, s: Secrets):
    global grafana_host
    global grafana_port
    global grafana_annotation_api_endpoint
    global grafana_user
    global grafana_pass

    global exp_start_time
    global exp_end_time
    global dashboardId

    # defaults
    grafana_user = c.get('grafana_user', 'admin')
    grafana_pass = c.get('grafana_pass', 'admin')
    grafana_host = c.get('grafana_host', 'localhost')
    grafana_port = c.get('grafana_port', 3000)
    grafana_annotation_api_endpoint = '/api/annotations'
    exp_start_time  = int(round(time.time() * 1000))
    exp_end_time    = int(round(time.time() * 1000))
    dashboardId = 5

    return 1


# Note: annotation region around the experiment is sent
# at experiment end
def before_experiment_control(context: dict, arguments=None):
#     import pdb; pdb.set_trace()
    d = datetime.now()
    mill = int(d.microsecond/1000)
    exp_start_time = int(round(time.time() * 1000)) + mill
    return 1


def after_experiment_control(context: dict, arguments=None):
#     import pdb; pdb.set_trace()
    exp_end_time = int(round(time.time() * 1000))

    tags = [ context['title'] ]
    text = context['description']

    payload = {
      "dashboardId": dashboardId,
      "time": exp_start_time,
      "isRegion": True,
      "timeEnd": exp_end_time,
      "tags": tags,
      "text": text
    }

    return post_event(payload)


def before_method_control(context: dict, arguments=None):

#     import pdb; pdb.set_trace()
    tags = [ context['description'] ]
    text = 'Start: ' + context['title']

    payload = {
      "dashboardId": dashboardId,
#       "time": int(round(time.time() * 1000)),
      "tags": tags,
      "text": text
    }

    return post_event(payload)

def after_method_control(context: dict, arguments=None):

#     import pdb; pdb.set_trace()
    tags = [ context['description'] ]
    text = 'End: ' + context['title']

    payload = {
      "dashboardId": dashboardId,
#       "time": int(round(time.time() * 1000)),
      "tags": tags,
      "text": text
    }

    return post_event(payload)

def before_activity_control(context: dict, arguments=None):

#     import pdb; pdb.set_trace()
    tags = [ context['type'], context['name'] ]
    text = f"[before][{context['type']}]:{context['name']}"

    payload = {
      "dashboardId": dashboardId,
#       "time": int(round(time.time() * 1000)),
      "tags": tags,
      "text": text
    }

    return post_event(payload)

def after_activity_control(context: dict, arguments=None):

#     import pdb; pdb.set_trace()
    tags = [ context['type'], context['name'] ]
    text = f"[after][{context['type']}]:{context['name']}"

    payload = {
      "dashboardId": dashboardId,
#       "time": int(round(time.time() * 1000)),
      "tags": tags,
      "text": text
    }

    return post_event(payload)


def post_event(payload):

    headers = {
        'Accept': 'application/json', 
        'Content-Type': 'application/json'
    }

    r = requests.post("http://{}:{}{}".format(
        grafana_host,
        grafana_port,
        grafana_annotation_api_endpoint),
        auth=HTTPBasicAuth(grafana_user, grafana_pass),
        headers=headers,
        data=json.dumps(payload))
    
    return r.status_code