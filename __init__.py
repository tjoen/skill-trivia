from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import requests
import json
import random
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
                self.speak(str(i) + "." + a)
            response = self.get_response('what.is.your.answer', on_fail="self.speak('Please say that again')", num_retries=2)
            if not response:
                return  # cancelled
	    LOGGER.debug("The response data is: {}".format(response))
            #answer = message.data["utterance"]
            self.speak("Your choice is "+ response)        
            if right_answer == allanswers[int(response)-1]:
                self.speak(random.choice(right))
                score = score+1
            else:
                self.speak(random.choice(wrong))
                self.speak("The answer is "+right_answer)        
        self.speak("You answered " +str(score)+ " questions correct")

    def stop(self):
        pass

def create_skill():
    return TriviaSkill()










