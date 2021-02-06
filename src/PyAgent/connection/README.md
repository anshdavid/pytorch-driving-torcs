# SNAKE OIL ( Chris X Edwards )

server client implementation is based on **Snake Oil**. Snake Oil is a Python library for interfacing with a TORCS 
race car simulator which has been patched with the server extentions used in the Simulated Car Racing competitions.

For further information please refer to 
1. [SnakeOil](http://xed.ch/p/snakeoil/)
2. [SCRC 2015 Software](https://cs.adelaide.edu.au/~optlog/SCR2015/software.html)

>
    /-----------------------------------------------\
    |!/usr/bin/python                              |
    |import snakeoil                                |
    |if __name__ == "__main__":                     |
    |    C= snakeoil.Client()                       |
    |    for step in xrange(C.maxSteps,0,-1):       |
    |        C.get_servers_input()                  |
    |        snakeoil.drive_example(C)              |
    |        C.respond_to_server()                  |
    |    C.shutdown()                               |
    \-----------------------------------------------/