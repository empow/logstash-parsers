# class node
# name - unique string identifier
# rank - topological sort rank
# outgoingAdjacent - dictionary on outgoing adjacent
# missingAllOutput - all the output pipelines are missing (and there is at list one output
# missingOutput - at least one output pipelines is missing (and there is at list one output
# missingAllInput - all the input pipelines are missing (and there is at list one input
# missingInput - at least one input pipelines is missing (and there is at list one input
# style (for graphviz):
#    filled
#    dashed - all input are missing
# shape (for graphviz):
#    circle: input/output
#    rectagle: pipeline
# color (for graphviz):
#    red: at least one output pipeline does not connected or file not found
#    orange: at least one input pipeline does not connected
#    grey: well connected node
class Node(object):
    def __init__(self, name, style="filled", shape="circle", color="grey", missingAllOutput=False, missingOutput=False, missingAllInput=False, missingInput=False):
        self._name=name
        self._rank=0
        self._outgoingAdjacent=[]
        self._missingAllOutput=missingAllOutput
        self._missingOutput=missingOutput
        self._missingAllInput=missingAllInput
        self._missingInput=missingInput
        self._style=style
        self._shape=shape
        self._color=color
        self._position_x=-1
        self._position_y=-1
    
    def getName(self):
        return self._name
        
    def addOutgoingAdjacent(self, name):
        self._outgoingAdjacent.append(name)
    def removeOutgoingAdjacent(self, name):
        self._outgoingAdjacent.remove(name)
    def getOutgoingAdjacent(self):
        return self._outgoingAdjacent
    def isSink():
        return len(self._outgoingAdjacent)==0


    def setRank(self, rank):
        self._rank=rank
    def getRank(self):
        return self._rank

    def setStyle(self, style):
        self._style=style
    def getStyle(self):
        return self._style

    def setShape(self, shape):
        self._shape=shape
    def getShape(self):
        return self._shape

    def setColor(self, color):
        self._color=color
    def getColor(self):
        return self._color

    def setMissingAllOutput(self, flag):
        self._missingAllOutput=flag
    def getMissingAllOutput(self):
        return self._missingAllOutput

    def setMissingAllInput(self, flag):
        self._missingAllInput=flag
    def getMissingAllInput(self):
        return self._missingAllInput
        
    def setMissingOutput(self, flag):
        self._missingAllOutput=flag
    def getMissingOutput(self):
        return self._missingAllOutput

    def setMissingInput(self, flag):
        self._missingAllInput=flag
    def getMissingInput(self):
        return self._missingAllInput

    def setPosition(self, x, y):
        self._position_x=x
        self._position_y=y
    def getPosition(self):
        return (self._position_x, self._position_y)
     
def hasCycle(nodes):
    tmp_nodes={}
    for v in nodes:
        u=[u for u in nodes[v].getOutgoingAdjacent() if u in nodes]
        tmp_nodes[v]=u

    while(True):
        t = [n for n in tmp_nodes if len(tmp_nodes[n])==0]
        if(len(t)==0):
            break
        for i in t:
            del tmp_nodes[i]
            for v in tmp_nodes:
                if i in tmp_nodes[v]:
                    tmp_nodes[v].remove(i)

    if len(tmp_nodes)==0:
        return False
    return True

def printGraph(nodes):
    for v in nodes:
        print v, nodes[v].getOutgoingAdjacent()
