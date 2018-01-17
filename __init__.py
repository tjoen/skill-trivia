from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import requests
import json
import random
import time
from subprocess import Popen, PIPE
from HTMLParser import HTMLParser

__author__ = 'tjoen'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

class TriviaSkill(MycroftSkill):
    def __init__(self):
        super(TriviaSkill, self).__init__("TriviaSkill")

    def initialize(self):
	trivia_intent = IntentBuilder("TriviaIntent").\
            require("TriviaKeyword").build()
        self.register_intent(trivia_intent, self.handle_trivia_intent)
	
    def play(self, filename):
        p = Popen(["aplay", self.settings.get('resdir')+filename ], stdout=PIPE, stderr=PIPE)
        p.communicate()
	
    def score(self, point):
        score = score+point
	return

    def wrong(self, right_answer):
        self.speak(random.choice(wrong))
        self.play( 'false.wav' )
        self.speak("The answer is "+right_answer)
	return

    def right(self):
        self.speak(random.choice(right))
	self.play( 'true.wav' )
        self.score(1)
        time.sleep(1)
	return	

    def preparequestion(self, category, question, answers, right_answer):
        quest = h.unescape( question )
        self.speak("The category is "+ category+ ". " + quest )
        correct_answer = h.unescape( right_answer )
        allanswers = list()
        allanswers.append(h.unescape(right_answer))
        for a in answers:
            allanswers.append(h.unescape(a))
        random.shuffle(allanswers)
	self.askquestion( category,quest, allanswers, correct_answer)

    def askquestion(self, category,quest, allanswers, correct_answer):
        i=0
	response = None
        for a in allanswers:
		i = i + 1
                self.speak(str(i) + ".    " + a)
	    #self.play( 'think.wav' )
	time.sleep(3)
	reponse = self.getinput()	
        LOGGER.debug("The response data is: {}".format(response))
        self.speak("Your choice is "+ response)        
        if correct_answer == allanswers[int(response)-1]:
            self.right()
        else:
            self.wrong(self, correct_answer)
	return 

    def getinput(self):
            response = self.get_response('what.is.your.answer')
	    if response:
                if response == 'free' or response == 'tree':
	            reponse = 3
	        if response == 'to':
		    response = 2
	        if response == 'for':
		    response = 4
		return response
	    else:
		self.getinput()

    def endgame(self, score):
        self.play( 'end.wav' )
        self.speak("You answered " +str(score)+ " questions correct")
        self.speak("Thanks for playing!")

    def handle_trivia_intent(self, message):
	self.settings['question'] = None
	self.settings['answers'] = None
	self.settings['answers'] = None
	self.settings['resdir'] = '/opt/mycroft/skills/skill-trivia/res/'
        url = "https://opentdb.com/api.php?amount=5&type=multiple"
        headers = {'Accept': 'text/plain'}
        r = requests.get(url, headers)
        h = HTMLParser()
        m = json.loads(r.text)
        questions = m['results'];
        score = 0
        right = ['Right!', 'That is correct', 'Yes, you are right', 'That is the right answer', 'Yes, good answer', 'Excellent choice']
        wrong = ['That is incorrect', 'Wrong answer', 'Sorry, you are wrong', 'That is not the right answer', 'You are wrong']
        self.play( 'intro.wav' )
	self.speak("Okay, Let's play a game of trivia. Get ready!")
	time.sleep(3)
	for f in questions:
            self.preparequestion( f['category'], f['question'], f['incorrect_answers'], f['correct_answer'])
        self.endgame(score)

    def stop(self):
        self.endgame(score)
        pass

def create_skill():
    return TriviaSkill()
