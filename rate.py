import os
import cherrypy
import sp

class Speech(object):
    @cherrypy.expose
    def index(self):
        return file("index.html")

class SpeechWebService(object):
	exposed = True

	def POST(self, file):
	# def POST(self, length=8):
	    score, feedback = sp.rate_vowel(file.file, 'M', 'ae')
	    return str(score)

if __name__ == '__main__':
	conf = {
		'/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/rate': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
	webapp = Speech()
	webapp.rate = SpeechWebService()
	cherrypy.quickstart(webapp, '/', conf)
