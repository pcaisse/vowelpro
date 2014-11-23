import traceback
import os
import cherrypy
from vowelpro import vowel
import json


# Absolute directory path of this file.
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = 'log'


class Speech(object):
    @cherrypy.expose
    def index(self):
        return file(os.path.join(DIR_PATH, "index.html"))

class SpeechWebService(object):
    exposed = True

    def POST(self, file, vowel_str):
        try:
            return json.dumps(vowel.rate_vowel(file.file, vowel_str))
        except Exception as e:
            cherrypy.log(e, traceback=True)
            return json.dumps({
                'error': str(e)
            })

# Set up logging.
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

cherrypy.config.update({
    'log.access_file': os.path.join(LOG_PATH, 'access.log'),
    'log.error_file': os.path.join(LOG_PATH, 'error.log')
})

# Configure app.
conf = {
    '/': {
        'tools.sessions.on': True,
        'tools.staticdir.root': DIR_PATH
    },
    '/rate': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'application/json')],
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'static'
    }
}

webapp = Speech()
webapp.rate = SpeechWebService()
cherrypy.quickstart(webapp, '/', conf)
