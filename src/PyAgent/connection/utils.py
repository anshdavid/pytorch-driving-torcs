import sys

PI= 3.14159265359
DataSize = 2**17

# Initialize help messages
# ophelp=  'Options:\n'
# ophelp+= ' --host, -H <host>    TORCS server host. [localhost]\n'
# ophelp+= ' --port, -p <port>    TORCS port. [3001]\n'
# ophelp+= ' --id, -i <id>        ID for server. [SCR]\n'
# ophelp+= ' --steps, -m <#>      Maximum simulation steps. 1 sec ~ 50 steps. [100000]\n'
# ophelp+= ' --episodes, -e <#>   Maximum learning episodes. [1]\n'
# ophelp+= ' --track, -t <track>  Your name for this track. Used for learning. [unknown]\n'
# ophelp+= ' --stage, -s <#>      0=warm up, 1=qualifying, 2=race, 3=unknown. [3]\n'
# ophelp+= ' --debug, -d          Output full telemetry.\n'
# ophelp+= ' --help, -h           Show this help.\n'
# ophelp+= ' --version, -v        Show current version.'
# usage= 'Usage: %s [ophelp [optargs]] \n' % sys.argv[0]
# usage= usage + ophelp
# version= "20130505-2"


def clip(v,lo,hi):
    if v<lo: return lo
    elif v>hi: return hi
    else: return v


def bargraph(x,mn,mx,w,c='X'):
    '''Draws a simple asciiart bar graph. Very handy for
    visualizing what's going on with the data.
    x= Value from sensor, mn= minimum plottable value,
    mx= maximum plottable value, w= width of plot in chars,
    c= the character to plot with.'''
    if not w: return '' # No width!
    if x<mn: x= mn      # Clip to bounds.
    if x>mx: x= mx      # Clip to bounds.
    tx= mx-mn # Total real units possible to show on graph.
    if tx<=0: return 'backwards' # Stupid bounds.
    upw= tx/float(w) # X Units per output char width.
    if upw<=0: return 'what?' # Don't let this happen.
    negpu, pospu, negnonpu, posnonpu= 0,0,0,0
    if mn < 0: # Then there is a negative part to graph.
        if x < 0: # And the plot is on the negative side.
            negpu= -x + min(0,mx)
            negnonpu= -mn + x
        else: # Plot is on pos. Neg side is empty.
            negnonpu= -mn + min(0,mx) # But still show some empty neg.
    if mx > 0: # There is a positive part to the graph
        if x > 0: # And the plot is on the positive side.
            pospu= x - max(0,mn)
            posnonpu= mx - x
        else: # Plot is on neg. Pos side is empty.
            posnonpu= mx - max(0,mn) # But still show some empty pos.
    nnc= int(negnonpu/upw)*'-'
    npc= int(negpu/upw)*c
    ppc= int(pospu/upw)*c
    pnc= int(posnonpu/upw)*'_'
    return '[%s]' % (nnc+npc+ppc+pnc)


# == Misc Utility Functions
def Destringify(s):
    '''makes a string into a value or a list of strings into a list of
    values (if possible)'''
    if not s: return s
    if type(s) is str:
        try:
            return float(s)
        except ValueError:
            print("Could not find a value in %s" % s)
            return s
    elif type(s) is list:
        if len(s) < 2:
            return Destringify(s[0])
        else:
            return [Destringify(i) for i in s]
