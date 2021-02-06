import logging

from src.logger import logger
from src.PyAgent.connection.utils import bargraph, clip

logger = logging.getLogger(__name__)

class DriverAction():
    # Composes something like this for the server:
    # (accel 1)(brake 0)(gear 1)(steer 0)(clutch 0)(focus 0)(meta 0) or
    # (accel 1)(brake 0)(gear 1)(steer 0)(clutch 0)(focus -90 -45 0 45 90)(meta 0)

    def __init__(self):
       self.actionstr= str()
       # "d" is for data dictionary.
       self.actionDict = {
            'accel':0.2,
            'brake':0,
            'clutch':0,
            'gear':1,
            'steer':0,
            'focus':[-90,-45,0,45,90],
            'meta':0}

    def ClipToLimits(self):
        # There pretty much is never a reason to send the server
        # something like (steer 9483.323). This comes up all the time
        # and it's probably just more sensible to always clip it than to
        # worry about when to. The "clip" command is still a snakeoil
        # utility function, but it should be used only for non standard
        # things or non obvious limits (limit the steering to the left,
        # for example). For normal limits, simply don't worry about it.

        self.actionDict['steer']= clip(self.actionDict['steer'], -1, 1)
        self.actionDict['brake']= clip(self.actionDict['brake'], 0, 1)
        self.actionDict['accel']= clip(self.actionDict['accel'], 0, 1)
        self.actionDict['clutch']= clip(self.actionDict['clutch'], 0, 1)

        if self.actionDict['gear'] not in [-1, 0, 1, 2, 3, 4, 5, 6]:
            self.actionDict['gear']= 0

        if self.actionDict['meta'] not in [0,1]:
            self.actionDict['meta']= 0

        if type(self.actionDict['focus']) is not list or \
            min(self.actionDict['focus'])<-180 or \
            max(self.actionDict['focus'])>180:
            self.actionDict['focus']= 0


    def __repr__(self):
        self.ClipToLimits()
        out= str()
        for k in self.actionDict:
            out+= '('+k+' '
            v= self.actionDict[k]
            if not type(v) is list:
                out+= '%.3f' % v
            else:
                out+= ' '.join([str(x) for x in v])
            out+= ')'
        return out


    def FancyOut(self):
        '''Specialty output for useful monitoring of bot's effectors.'''
        out= str()
        od= self.actionDict.copy()
        od.pop('gear','') # Not interesting.
        od.pop('meta','') # Not interesting.
        od.pop('focus','') # Not interesting. Yet.
        for k in sorted(od):
            if k == 'clutch' or k == 'brake' or k == 'accel':
                strout=''
                strout= '%6.3f %s' % (od[k], bargraph(od[k],0,1,50,k[0].upper()))
            elif k == 'steer': # Reverse the graph to make sense.
                strout= '%6.3f %s' % (od[k], bargraph(od[k]*-1,-1,1,50,'S'))
            else:
                strout= str(od[k])
            out+= "%s: %s\n" % (k,strout)
        return out
