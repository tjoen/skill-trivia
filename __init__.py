from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
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

validmc = [ '1', '2', '3', '4']
score = 0

class TriviaSkill(MycroftSkill):
    def __init__(self):
        super(TriviaSkill, self).__init__(name="TriviaSkill")

    def initialize(self):
        super(TriviaSkill, self).initialize()
    
    def play(self, filename):
        play_wav( self.settings.get('resdir')+filename )
    
    def score(self, point):
        global score
        score = score+point
        return

    def wrong(self, right_answer):
        self.enclosure.mouth_text( "WRONG!" )
        self.speak_dialog("incorrect")
        wait_while_speaking()
        self.play( 'false.wav' )
        self.speak("The answer is "+right_answer)
        wait_while_speaking()
        return

    def right(self):
        self.enclosure.mouth_text( "CORRECT!" )
        self.speak_dialog("correct")
        wait_while_speaking()
        self.play( 'true.wav' )
        self.score(1)
        return    

    def preparequestion(self, category, question, answers, right_answer):
        self.enclosure.activate_mouth_events()
        self.enclosure.mouth_reset()
        h = HTMLParser()
        quest = h.unescape( question )
        time.sleep(1.5)
        self.speak("The category is "+ category+ ". " + quest )
        wait_while_speaking()
        correct_answer = h.unescape( right_answer )
        allanswers = list()
        allanswers.append(h.unescape(right_answer))
        for a in answers:
            allanswers.append(h.unescape(a))
        random.shuffle(allanswers)
        self.settings['cat'] = category
        self.settings['question'] = quest
        self.settings['answers'] = allanswers
        self.settings['correct_answer'] = correct_answer
        self.askquestion( category, quest, allanswers, correct_answer )
    
    def repeatquestion(self, category, question, answers, right_answer):
        time.sleep(1)
        self.speak("The category is "+category+". "+ question )
        wait_while_speaking()
        i=0
        ans = ""
        for a in answers:
            i = i + 1
            self.speak(str(i) + ".    " + a)
            wait_while_speaking()
        #ans = ans+("|"+str(i)+"|"+a)
        #self.enclosure.mouth_text( ans )
        self.getinput()
        return

    def askquestion( self, category, quest, allanswers, correct_answer):
        i=0
        ans = ""
        for a in allanswers:
            i = i + 1
            self.speak(str(i) + ".    " + a)
            wait_while_speaking()
            #ans = ans+("|"+str(i)+">"+a)
        #self.enclosure.mouth_text( ans )
        self.getinput()
        response = self.settings.get('myanswer')
        self.speak("Your choice is "+ str(response))
        wait_while_speaking()
        self.enclosure.deactivate_mouth_events()
        if correct_answer == allanswers[int(response)-1]:
            self.right()
        else:
            self.wrong(correct_answer)
        return 

    def getinput(self):
        self.settings['myanswer'] = None
        def is_valid(utt):
            #print ( 'utterance ='+ str(utt) )
            try:
                return 1 <= int(utt) <= 4
            except:
                return False
     
        r = self.get_response('what.is.your.answer')
        wait_while_speaking()        
        LOGGER.info('Trivia-skill: reply = ' + str(r))
        
        if r is None:
            self.speak('Did not get an answer.')
            wait_while_speaking()
            self.getinput()       
        else:
            LOGGER.info('Trivia-skill: r = ' + str(r))
            if r in validmc:
                self.settings['myanswer'] = str(r)
                LOGGER.info('Trivia-skill: r seems valid = ' + str(r))
                return
            elif r == 'repeat':
                self.speak('I will repeat the question')
                wait_while_speaking()
                self.repeatquestion( self.settings.get('cat'), self.settings.get('question'), self.settings.get('answers'), self.settings.get('correct_answer'))
            else:
                self.speak('Sorry. I did not understand ' + str(r) )
                LOGGER.info('Trivia-skill: r seems invalid = ' + str(r))
                wait_while_speaking()
                self.getinput()   

    def endgame(self, score):
        self.enclosure.deactivate_mouth_events()
        self.play( 'end.wav' )
        self.enclosure.mouth_text( "SCORE: "+str(score) )
        self.speak("You answered " +str(score)+ " questions correct")
        wait_while_speaking()
        self.speak("Thanks for playing!")
        wait_while_speaking()
        self.stop()
    
    def handle_trivia_intent(self):
        self.enclosure.deactivate_mouth_events()
        # Display icon on faceplate
        self.enclosure.mouth_display("aIMAMAMPMPMPMAMAAPAPADAAIOIOAAAHAMAMAHAAIOIOAAAPAFAFAPAAMLMLAAAAAA", x=1, y=0, refresh=True)
        time.sleep(2) 
        self.settings['cat'] = None
        self.settings['question'] = None
        self.settings['answers'] = None
        self.settings['myanswer'] = None
        self.settings['correct_answer'] = None
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
        for f in questions:
            self.enclosure.activate_mouth_events()
            self.enclosure.mouth_reset()
            self.preparequestion( f['category'], f['question'], f['incorrect_answers'], f['correct_answer'])
        self.endgame(score)
    
    def stop(self):
        self.enclosure.activate_mouth_events()
        self.enclosure.mouth_reset()
        self.enclosure.reset()    
        pass

    @intent_handler(IntentBuilder("TriviaIntent").require("TriviaKeyword"))
    def detect_trivia_intent(self, message):
        self.handle_trivia_intent()

def create_skill():
    return TriviaSkill()
