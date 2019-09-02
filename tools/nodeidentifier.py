import re
# extract idenfifier from both input and output
# E.g.:
#        from udp/tcp input: the port number
#        from elasticsearch output the hosts (multiple identifiers)
class NodeId(object):
    def __init__(self):
        pass
    def getNodeIdentifier(self, tokens):
        return []

# extract simple idenfifier containing just the prefix
class NodeIdSimple(NodeId):
    def __init__(self, prefix):
        self._prefix=prefix
    def getNodeIdentifier(self, tokens):
        return [self._prefix]

# extract a list of idenfifier from the location based on a regex
class NodeIdList(NodeId):
    def __init__(self, prefix, location, regex):
        if(len(prefix)==0 or location == None):
            self._prefix=prefix
        else:
            self._prefix=prefix + "-"
        self._location=location
        self._regex=regex
    def getNodeIdentifier(self, tokens):
        locationFlag=False # indicates if the location of the identifier has been found
        for i in xrange(len(tokens)):
            locationFlag=True
            for j in xrange(len(self._location)):
                if(i+j>len(tokens) or tokens[i+j]!=self._location[j]):
                    locationFlag=False
                    break
            if locationFlag==True:
                break

        if locationFlag==False:
            return [self._prefix]

        s=i+len(self._location)
        j=0
        while(True):
            if(tokens[i+len(self._location)+j]==']'):
                break
            j+=1
        e=i+len(self._location)+j
        txt=''.join(tokens[s+1:e])
        x=re.findall(self._regex, txt)
        idList=[]
        for i in x:
            idList.append(self._prefix+i)
        return idList

#extract a simple and single field that come just after the location
class NodeIdSingleField(NodeId):
    def __init__(self, prefix, location):
        if(len(prefix)==0 or location == None):
            self._prefix=prefix
        else:
            self._prefix=prefix + "-"
        self._location=location

    def getNodeIdentifier(self, tokens):
        locationFlag=False # indicates if the location of the identifier has been found
        for i in xrange(len(tokens)):
            locationFlag=True
            for j in xrange(len(self._location)):
                if(i+j>len(tokens) or tokens[i+j]!=self._location[j]):
                    locationFlag=False
                    break
            if locationFlag==True:
                break

        if locationFlag==False:
            return [self._prefix]

        return [self._prefix+tokens[i+len(self._location)]]

#extract a single field consisting of multiple values that come just after each location
class NodeIdMultipleFields(NodeId):
    def __init__(self, prefix, location):
        if(len(prefix)==0 or location == None):
            self._prefix=prefix
        else:
            self._prefix=prefix + "-"
        self._location=location

    def getNodeIdentifier(self, tokens):
        idList=[]
        for loc in self._location:
            locationFlag=False # indicates if the location of the identifier has been found
            for i in xrange(len(tokens)):
                locationFlag=True
                for j in xrange(len(loc)):
                    if(i+j>len(tokens) or tokens[i+j]!=loc[j]):
                        locationFlag=False
                        break
                if locationFlag==True:
                    break

            if locationFlag==True:
                idList.append(tokens[i+len(loc)])

        return [self._prefix+ '-'.join(idList)]
