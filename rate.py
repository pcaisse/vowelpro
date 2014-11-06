import traceback
import os
import cherrypy
import sp
import json

class Speech(object):
    @cherrypy.expose
    def index(self):
        return file("index.html")

class SpeechWebService(object):
    exposed = True

    def POST(self, file, sex, vowel):
        try:
            score, feedback = sp.rate_vowel(file.file, sex, vowel)
            return json.dumps({
                'score': str(score),
                'feedback': feedback 
            })
        except Exception as e:
            print traceback.format_exc()
            return json.dumps({
                'error': str(e)
            })

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/rate': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'js'
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'css'
        }
    }
    webapp = Speech()
    webapp.rate = SpeechWebService()
    cherrypy.quickstart(webapp, '/', conf)
