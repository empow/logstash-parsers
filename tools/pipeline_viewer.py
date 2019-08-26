# Licensed to empow under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. empow licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import sys
import yaml
import Queue
import optparse

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from graphviz import Digraph
import graphviz
import re


# print colored text of terminal
def colored(s, fg="default", style="normal", bg="default"):
    base="\033[m"
    scheme="\033[%s;%s%sm"
    fg_map={}
    fg_map["default"]=""
    fg_map["black"]="30"
    fg_map["red"]="31"
    fg_map["green"]="32"
    fg_map["yellow"]="33"
    fg_map["blue"]="34"
    fg_map["purple"]="35"
    fg_map["cyan"]="36"
    fg_map["white"]="37"
    fg_map["gray"]="38"

    bg_map={}
    bg_map={}
    bg_map["default"]=""
    bg_map["black"]=";40"
    bg_map["red"]=";41"
    bg_map["green"]=";42"
    bg_map["yellow"]=";43"
    bg_map["blue"]=";44"
    bg_map["purple"]=";45"
    bg_map["cyan"]=";46"
    bg_map["white"]=";47"
    bg_map["gray"]=";48"
    
    style_map={}
    style_map["normal"]="0"
    style_map["bold"]="1"
    style_map["underline"]="2"
    style_map["negative"]="3"
    
    fg_color=""
    if fg in fg_map:
        fg_color=fg_map[fg]

    bg_color=""
    if bg in bg_map:
        bg_color=bg_map[bg]

    text_style="0"
    if style in style_map:
        text_style=style_map[style]
        
    c=scheme % (text_style, fg_color, bg_color)
    return "%s%s%s" % (c, s, base)


def print_errors(errors):
    for (m,i) in errors:
        if i=="error":
            print colored("ERROR: " + m, "red", "bold")
        elif i=="warning":
            print colored("WARN:  " + m, "red", "bold")
        else:
            print colored("INFO:  " + m)
        

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
        self.prefix=prefix
    def getNodeIdentifier(self, tokens):
        return [self.prefix]

# extract a list of idenfifier from the location based on a regex
class NodeIdList(NodeId):
    def __init__(self, prefix, location, regex):
        if(len(prefix)==0 or location == None):
            self.prefix=prefix
        else:
            self.prefix=prefix + "-"
        self.location=location
        self.regex=regex
    def getNodeIdentifier(self, tokens):
        locationFlag=False # indicates if the location of the identifier has been found
        for i in xrange(len(tokens)):
            locationFlag=True
            for j in xrange(len(self.location)):
                if(i+j>len(tokens) or tokens[i+j]!=self.location[j]):
                    locationFlag=False
                    break
            if locationFlag==True:
                break

        if locationFlag==False:
            return [self.prefix]

        s=i+len(self.location)
        j=0
        while(True):
            if(tokens[i+len(self.location)+j]==']'):
                break
            j+=1
        e=i+len(self.location)+j
        txt=''.join(tokens[s+1:e])
        x=re.findall(self.regex, txt)
        idList=[]
        for i in x:
            idList.append(self.prefix+i)
        return idList

#extract a simple and single field that come just after the location
class NodeIdSingleField(NodeId):
    def __init__(self, prefix, location):
        if(len(prefix)==0 or location == None):
            self.prefix=prefix
        else:
            self.prefix=prefix + "-"
        self.location=location

    def getNodeIdentifier(self, tokens):
        locationFlag=False # indicates if the location of the identifier has been found
        for i in xrange(len(tokens)):
            locationFlag=True
            for j in xrange(len(self.location)):
                if(i+j>len(tokens) or tokens[i+j]!=self.location[j]):
                    locationFlag=False
                    break
            if locationFlag==True:
                break

        if locationFlag==False:
            return [self.prefix]

        return [self.prefix+tokens[i+len(self.location)]]

#extract a single field consisting of multiple values that come just after each location
class NodeIdMultipleFields(NodeId):
    def __init__(self, prefix, location):
        if(len(prefix)==0 or location == None):
            self.prefix=prefix
        else:
            self.prefix=prefix + "-"
        self.location=location

    def getNodeIdentifier(self, tokens):
        idList=[]
        for loc in self.location:
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

        return [self.prefix+ '-'.join(idList)]
class Pipeline(object):
    def __init__(self, filename):
        f=open(filename, 'r')
        self.t=[]
        for l in f.readlines():
            tokens = word_tokenize(l)
            # remove comments
            for i in xrange(len(tokens)):
                if(tokens[i]=="#"):
                    tokens=tokens[:i]
                    break
            self.t+=tokens
            (self.p1, self.p2) = Pipeline.parenthesis(self.t)
            if(self.p1==None):
                self.t=[]
                return

        self.input_index=self.filter_index=self.output_index=None
        for i in xrange(len(self.t)):
            if self.t[i]=="input":
                self.input_index=i+1
            elif self.t[i]=="filter":
                self.filter_index=i+1
            elif self.t[i]=="output":
                self.output_index=i+1

    @staticmethod
    def parenthesis(x):
        q=Queue.LifoQueue()
        p1={}
        p2={}

        for i in xrange(len(x)):
            if x[i] in ['(', '[', '{']:
                q.put(i);
                continue
            if x[i] in [')', ']', '}']:
                if(q.empty()==True):
                    return (None, None)
                k=q.get(False)
                p1[k]=i
                p2[i]=k
                continue

        return (p1, p2)

    
    def get_input(self):
        if self.input_index==None:
            return None
        return self.t[self.input_index: self.p1[self.input_index]]
        
    def get_filter(self):
        if self.filter_index==None:
            return None
        return self.t[self.filter_index: self.p1[self.filter_index]]

    def get_output(self):
        if self.output_index==None:
            return None
        return self.t[self.output_index: self.p1[self.output_index]]


    def list_of_inputs(self, nodeId):
        x=self.get_input()
        (p1, p2) = Pipeline.parenthesis(x)
        l=[]
        i=1
        
        input_list=[]

        while(i<len(x)):
            t=x[i]+"_input"
            if t in nodeId:
                ttt = nodeId[t]
                n=ttt.getNodeIdentifier(x[i+1:p1[i+1]])
                for v in n:
                    input_list.append((x[i], v))
                i=p1[i+1]+1
            else:
                i+=1

        return input_list


    def list_of_outputs(self, nodeId):
        x=self.get_output()
        (p1, p2) = Pipeline.parenthesis(x)
        l=[]
        i=1

        output_list=[]
        while(i<len(x)):
            t=x[i]+"_output"
            if t in nodeId:
                ttt = nodeId[t]
                n=ttt.getNodeIdentifier(x[i+1:p1[i+1]])
                for v in n:
                    output_list.append((x[i], v))
                i=p1[i+1]+1
            else:
                i+=1
                                    
        return output_list


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
        self.name=name
        self.rank=0
        self.outgoingAdjacent=[]
        self.missingAllOutput=missingAllOutput
        self.missingOutput=missingOutput
        self.missingAllInput=missingAllInput
        self.missingInput=missingInput
        self.style=style
        self.shape=shape
        self.color=color
    
    def addOutgoingAdjacent(self, name):
        self.outgoingAdjacent.append(name)
    
    def setRank(self, rank):
        self.rank=rank

    def setStyle(self, style):
        self.style=style

    def setShape(self, shape):
        self.shape=shape

    def setColor(self, color):
        self.color=color

    def setMissigAllOutput(self, flag):
        self.missingAllOutput=flag

    def setMissigAllInput(self, flag):
        self.missingAllInput=flag
        
    def setMissigOutput(self, flag):
        self.missingAllOutput=flag

    def setMissigInput(self, flag):
        self.missingAllInput=flag
     
def hasCycle(nodes):
    tmp_nodes={}
    for v in nodes:
        u=[u for u in nodes[v].outgoingAdjacent if u in nodes]
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
        print v, nodes[v].outgoingAdjacent

def main():

    parser = optparse.OptionParser()
    parser.add_option('-c', dest="filename", default="", help="full path of the pipeline.yml configuration file.")
    parser.add_option('-v', dest="verbose", default=False, action="store_true", help="prints various information useful for debugging.")

    (option, args)= parser.parse_args()

    # con (dict)
    # for each pipeline identifier: (list of input, list of output)
    # each element in the list list (input & output): (type, name)
    con={} 

    # out_node (dict)
    # for each pipeline to pipeline identifier: list of the pipeline in which this identifier is part of the output section
    out_node={}

    # in_node (dict)
    # for each pipeline to pipeline identifier: list of the pipeline in which this identifier is part of the input section
    in_node={}


    # nodes dictionary {node name: node object}
    nodes={}
    
    # a dict containing all the type of input/output to be analyzed
    nodeId={}

    # output identifiers
    n=NodeIdList("", ["send_to", "=", ">"], "(\w+)")
    nodeId["pipeline_output"]=n

    n=NodeIdList("elastic", ["hosts", "=", ">"], "\"([^:]*):\d+\"")
    nodeId["elasticsearch_output"]=n

    n=NodeIdMultipleFields("udp", [["port", "=", ">"], ["host", "=", ">", "\""]])
    nodeId["udp_output"]=n

    n=NodeIdMultipleFields("tcp", [["port", "=", ">"], ["host", "=", ">", "\""]])
    nodeId["tcp_output"]=n

    n=NodeIdSimple("stdout")
    nodeId["stdout_output"]=n


    # input identifiers
    n=NodeIdSingleField("", ["address", "=", ">"])
    nodeId["pipeline_input"]=n

    n=NodeIdSingleField("udp", ["port", "=", ">"])
    nodeId["udp_input"]=n

    n=NodeIdSingleField("tcp", ["port", "=", ">"])
    nodeId["tcp_input"]=n

    n=NodeIdSimple("stdin")
    nodeId["stdin_input"]=n

    n=NodeIdSingleField("beats", ["port", "=", ">"])
    nodeId["beats_input"]=n


    # list of error to be printed (if verbose is True)
    # each element: (message, error type) 
    # Type: info, warning, error

    errors=[]

    with open(option.filename, "r") as stream:
        try:
            for p in (yaml.safe_load(stream)):
                if 'path.config' in p.keys() and 'pipeline.id' in p.keys():
                    try:
                        a=Pipeline(p['path.config'])
                        con[p['pipeline.id']]=(a.list_of_inputs(nodeId), a.list_of_outputs(nodeId))
                    except Exception as e: 
                        errors.append((str(e), "error"))
                        node = Node(name=p['pipeline.id'], style="filled", shape="box", color="red", missingAllOutput=True, missingOutput=True, missingAllInput=True, missingInput=True)
                        nodes[p['pipeline.id']]=node
                        errors.append(("Pipeline %s cannot be parsed" % p['pipeline.id'], "error"))
                        
        except yaml.YAMLError as exc:
            print(exc)



    for n in con.keys():
        nodes[n]=[]
        node = Node(name=n, style="filled", shape="box", color="grey", missingAllOutput=False, missingAllInput=False)
        nodes[n]=node
        for (a,b) in con[n][0]:
            if(a=='pipeline'):
                if(b in in_node):
                    in_node[b].append(n)
                else:
                    in_node[b]=[n]
                
            else: # input/output node
                tmp=b
                if(tmp in nodes):
                    nodes[tmp].addOutgoingAdjacent(n)
                else:
                    tmp_node = Node(name=tmp, style="filled", shape="ellipse", color="grey", missingAllOutput=False, missingAllInput=False)
                    tmp_node.addOutgoingAdjacent(n)
                    nodes[tmp]=tmp_node

        for (a,b) in con[n][1]:
            if(a=='pipeline'):
                if(b in out_node):
                    out_node[b].append(n)
                else:
                    out_node[b]=[n]
            else:
                tmp = b
                nodes[n].addOutgoingAdjacent(tmp)

                tmp_node=Node(name=tmp, style="filled", shape="ellipse", color="grey", missingAllOutput=False, missingAllInput=False)
                nodes[tmp]=tmp_node



    tmp_out = [x[1] for p in con for x in con[p][1] if x[0]=="pipeline"]
    for p in con:
        tmp_in=[x[1] for x in con[p][0] if x[0]=="pipeline"] 
        if(set(tmp_in).issubset(tmp_out)==False): # missing an input
            nodes[p].setColor("orange")
            nodes[p].setMissigInput(True)
            errors.append(("Some of the input of pipeline %s are missing" % p, "info"))
        if(len(tmp_in)>0 and set(tmp_in).isdisjoint(tmp_out)==True): # missing all input
            nodes[p].setMissigAllInput(True)
            nodes[p].setColor("orange")
            nodes[p].setStyle("dashed")
            errors.append(("All the input of pipeline %s are missing (the pipeline is unused)" % p, "info"))

    tmp_in = [x[1] for p in con for x in con[p][0] if x[0]=="pipeline"]
    for p in con:
        tmp_out=[x[1] for x in con[p][1] if x[0]=="pipeline"] 
        if(set(tmp_out).issubset(tmp_in)==False): # missing an output
            nodes[p].setColor("red")
            nodes[p].setMissigOutput(True)
            errors.append(("Some of the output of pipeline %s are missing" % p, "error"))

        if(len(tmp_out)>0 and set(tmp_out).isdisjoint(tmp_in)==True): # missing all output
            nodes[p].setMissigAllOutput(True)
            print tmp_out, tmp_in
            errors.append(("All the output of pipeline %s are missing" % p, "error"))


    for a in in_node:
        if a in out_node:
            for x in in_node[a]:
                for y in out_node[a]:
                    nodes[y].addOutgoingAdjacent(x)


    in_deg={}
    for n in nodes:
        in_deg[n]=0

    for n in nodes:
        for i in nodes[n].outgoingAdjacent:
            in_deg[i]+=1
    nodes_rank={}
    rank=0

    tmp_nodes=dict.copy(nodes)

    while(len(tmp_nodes)>0):
        # find sources (first we search for well connected nodes)
        flag=False
        for n in in_deg:
            if in_deg[n]==0 and tmp_nodes[n].missingAllInput==False:
                flag=True
                nodes_rank[n]=rank

        # if well connected nodes were not found search for other nodes
        if(flag==False):
            for n in in_deg:
                if in_deg[n]==0:
                    flag=True
                    nodes_rank[n]=rank

        if(flag==False): # cycles exist!
            break
                    
        # remove ranked nodes
        for n in nodes_rank:
            if nodes_rank[n]==rank:
                for t in tmp_nodes[n].outgoingAdjacent:
                    in_deg[t]-=1
                del tmp_nodes[n]
                del in_deg[n]
        rank+=1

    g = Digraph(engine="dot", format='png')

    if(len(tmp_nodes)>0):  # cycles exists ! view it.
        # let's remove nodes in which their out degree is 0
        while(True):
            t = [n for n in tmp_nodes if len(tmp_nodes[n].outgoingAdjacent)==0]
            if(len(t)==0):
                break
            for i in t:
                del tmp_nodes[i]
                for v in tmp_nodes:
                    if i in tmp_nodes[v].outgoingAdjacent:
                        tmp_nodes[v].outgoingAdjacent.remove(i)


        tmp=dict.copy(tmp_nodes)
        for v in tmp_nodes:
            del tmp[v]
            if(hasCycle(tmp)==False):
                tmp[v]=tmp_nodes[v]
        
        
               
        for v in tmp:
            g.node(v, shape="box", style="filled", color="red")

        errors.append(("One or more cycles has been found", "error"))
        for v in tmp:
            for u in tmp[v].outgoingAdjacent:
                if u not in tmp:
                    continue
                g.edge(v, u, color="red")
        g.view()

    else: # no cycles
        ranks={}
        for n in nodes:
            r=nodes_rank[n]
            nodes[n].setRank(r)
            if r in ranks:
                ranks[r].append(n)
            else:
                ranks[r]=[n]
                
        m=0

        for i in ranks:
            if(len(ranks[i])>m):
                m=len(ranks[i])


        g = Digraph(engine="neato", format='png', graph_attr={'splines':"ortho"})


        for i in ranks:
            x=float(m)/(len(ranks[i])+1)
            x*=2
            j=0
            for n in ranks[i]:
                j+=x

                g.node(n, pos="%d,%d!" %(j, rank-i), shape=nodes[n].shape, style=nodes[n].style, color=nodes[n].color)
            
        for v in nodes:
            for u in nodes[v].outgoingAdjacent:
                g.edge(v, u)


        
    g.view()
    if(option.verbose==True):
        print_errors(errors)


main()
