from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.audio import wait_while_speaking
from mycroft.util import play_wav
from mycroft.util.log import getLogger
import requests
import json
import random
import time
from HTMLParser import HTMLParser

__author__ = 'tjoen'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

right = ['Right!', 'That is correct', 'Yes, you are right', 'That is the right answer', 'Yes, good answer', 'Excellent choice']
wrong = ['That is incorrect', 'Wrong answer', 'Sorry, you are wrong', 'That is not the right answer', 'You are wrong']
validmc = [ '1', '2', '3', '4']
score = 0

class TriviaSkill(MycroftSkill):
    def __init__(self):
        super(TriviaSkill, self).__init__("TriviaSkill")

    def initialize(self):
	trivia_intent = IntentBuilder("TriviaIntent").\
            require("TriviaKeyword").build()
        self.register_intent(trivia_intent, self.handle_trivia_intent)
	
    def play(self, filename):
        play_wav( self.settings.get('resdir')+filename )
	
    def score(self, point):
	global score
        score = score+point
	return

    def wrong(self, right_answer):
        self.speak(random.choice(wrong))
	wait_while_speaking()
        self.play( 'false.wav' )
        self.speak("The answer is "+right_answer)
	wait_while_speaking()
	return

    def right(self):
        self.speak(random.choice(right))
	wait_while_speaking()
	self.play( 'true.wav' )
        self.score(1)
	return	

    def preparequestion(self, category, question, answers, right_answer):
	h = HTMLParser()
        quest = h.unescape( question )
        text = quest
        self.speak("The category is "+ category+ ". " + quest )
	wait_while_speaking()
	self.enclosure.deactivate_mouth_events()
	self.enclosure.mouth_text(text)
        correct_answer = h.unescape( right_answer )
        allanswers = list()
        allanswers.append(h.unescape(right_answer))
        for a in answers:
            allanswers.append(h.unescape(a))
        random.shuffle(allanswers)
	self.askquestion( category, quest, allanswers, correct_answer )

    def askquestion( self, category, quest, allanswers, correct_answer):
        i=0
        ans = ""
        for a in allanswers:
		i = i + 1
                self.speak(str(i) + ".    " + a)
                ans = ans + str(i) + "." + a + "  "
		wait_while_speaking()
        self.enclosure.mouth_reset()
        self.enclosure.mouth_text(ans)
	response = self.getinput()
	self.enclosure.activate_mouth_events()
        self.enclosure.mouth_reset()
        self.speak("Your choice is "+ response)
	wait_while_speaking()
        if correct_answer == allanswers[int(response)-1]:
            self.right()
        else:
            self.wrong(correct_answer)
	return 

    def getinput(self):
            #response = None
            response = self.get_response('what.is.your.answer')
	    wait_while_speaking()
            if response:              
                if response == "1" or response == "wan":
                    response = 1
                elif response == "2" or response == "to":
    	            response = 2
                elif response == "3" or response == "tree" or response == "free":
    	            response = 3
                elif response == "4" or response == "for":
    	            response = 4	
            if response in validmc:
                return response
            else:
                self.speak( str(response)+ " is not a valid choice")
    	        wait_while_speaking()
                self.getinput()

    def endgame(self, score):
        self.play( 'end.wav' )
        self.speak("You answered " +str(score)+ " questions correct")
	wait_while_speaking()
        self.speak("Thanks for playing!")
        wait_while_speaking()
	
    def handle_trivia_intent(self, message):
	self.settings['question'] = None
	self.settings['answers'] = None
	self.settings['answers'] = None
	self.settings['resdir'] = '/opt/mycroft/skills/skill-trivia/res/'
        url = "https://opentdb.com/api.php?amount=5&type=multiple"
        headers = {'Accept': 'text/plain'}
        r = requests.get(url, headers)
        m = json.loads(r.text)
        questions = m['results'];
	global score
        score = 0
        self.play( 'intro.wav' )
	self.speak("Okay, lets play a game of trivia. Get ready!")
	wait_while_speaking()
	time.sleep(2)
	for f in questions:
            self.preparequestion( f['category'], f['question'], f['incorrect_answers'], f['correct_answer'])
        self.endgame(score)
	

    def stop(self):
        pass

def create_skill():
    return TriviaSkill()
