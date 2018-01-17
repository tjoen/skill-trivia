from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import requests
import json
import random
import time
import subprocess
from HTMLParser import HTMLParser

__author__ = 'tjoen'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

class TriviaSkill(MycroftSkill):
    def __init__(self):
        super(TriviaSkill, self).__init__("TriviaSkill")

    def initialize(self):
	self.settings['resdir'] = '/opt/mycroft/skills/skill-trivia/res/'
	trivia_intent = IntentBuilder("TriviaIntent").\
            require("TriviaKeyword").build()
        self.register_intent(trivia_intent, self.handle_trivia_intent)
	
    def play(self,filename):
        p = Popen(["aplay", filename ], stdout=PIPE, stderr=PIPE)
        p.communicate())
	
    def handle_trivia_intent(self, message):
        url = "https://opentdb.com/api.php?amount=5&type=multiple"
        headers = {'Accept': 'text/plain'}
        r = requests.get(url, headers)
        h = HTMLParser()
        m = json.loads(r.text)
        questions = m['results'];
        score = 0
        right = ['Right!', 'That is correct', 'Yes, you are right', 'That is the right answer', 'Yes, good answer', 'Excellent choice']
        wrong = ['That is incorrect', 'Wrong answer', 'Sorry, you are wrong', 'That is not the right answer', 'You are wrong']
        self.speak("Okay, Let's play a game of trivia. Get ready!")
	self.play( self.settings.get('resdir')+'intro.wav' )
	for f in questions:
            quest = h.unescape(f['question'])
            self.speak("The category is "+ f['category']+ ". " + quest + "\n" )
            right_answer = h.unescape(f['correct_answer'])
            allanswers = list()
            allanswers.append(h.unescape(f['correct_answer']))
            for a in f['incorrect_answers']:
                allanswers.append(h.unescape(a))
            random.shuffle(allanswers)
            i=0
            for a in allanswers:
		i = i + 1
                self.speak(str(i) + ".    " + a)
	    self.play( self.settings.get('resdir')+'think.wav' )
	    response = None
            response = self.get_response('what.is.your.answer', num_retries=4)
            if response == 'free':
	        reponse = 3
	    if response == 'to':
		response = 2
	    if response == 'for':
		response = 4
	    LOGGER.debug("The response data is: {}".format(response))
            self.speak("Your choice is "+ response)        
            if right_answer == allanswers[int(response)-1]:
                self.speak(random.choice(right))
		self.play( self.settings.get('resdir')+'true.wav' )
                score = score+1
		time.sleep(1)
            else:
                self.speak(random.choice(wrong))
		self.play( self.settings.get('resdir')+'false.wav' )
                self.speak("The answer is "+right_answer)
	self.play( self.settings.get('resdir')+'end.wav' )
        self.speak("You answered " +str(score)+ " questions correct")
	
    def stop(self):
        pass

def create_skill():
    return TriviaSkill()










