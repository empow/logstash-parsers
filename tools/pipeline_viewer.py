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

#local libraries
import nodeidentifier as ni
from node import Node, hasCycle

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
        



class Pipeline(object):

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
        if self._input_index==None:
            return None
        return self._t[self._input_index: self._p1[self._input_index]]
        
    def get_filter(self):
        if self._filter_index==None:
            return None
        return self._t[self._filter_index: self._p1[self._filter_index]]

    def get_output(self):
        if self._output_index==None:
            return None
        return self._t[self._output_index: self._p1[self._output_index]]



    def list_of_connections(self, nodeId, direction):
        if direction not in ["input", "output"]:
            return
        
        exec("x=self.get_%s()" % direction)
        (p1, p2) = Pipeline.parenthesis(x)
        l=[]
        i=1
        
        connection_list=[]

        while(i<len(x)):
            t=x[i]+"_%s" % direction
            if t in nodeId:
                ttt = nodeId[t]
                n=ttt.getNodeIdentifier(x[i+1:p1[i+1]])

                for v in n:
                    connection_list.append((x[i], v))
                i=p1[i+1]+1
            else:
                i+=1

        return connection_list

class PipelineFile(Pipeline):
    def __init__(self, filename):
        f=open(filename, 'r')
        self._t=[]
        for l in f.readlines():
            tokens = word_tokenize(l)
            # remove comments
            for i in xrange(len(tokens)):
                if(tokens[i]=="#"):
                    tokens=tokens[:i]
                    break
            self._t+=tokens
        
        (self._p1, self._p2) = Pipeline.parenthesis(self._t)
        if(self._p1==None):
            self._t=[]
            return

        self._input_index=self._filter_index=self._output_index=None
        for i in xrange(len(self._t)):
            if self._t[i]=="input":
                self._input_index=i+1
            elif self._t[i]=="filter":
                self._filter_index=i+1
            elif self._t[i]=="output":
                self._output_index=i+1


class PipelineString(Pipeline):
    def __init__(self, s):
        tokens = word_tokenize(s)
        # remove comments
        for i in xrange(len(tokens)):
            if(tokens[i]=="#"):
                tokens=tokens[:i]
                break
        self._t=tokens


        (self._p1, self._p2) = Pipeline.parenthesis(self._t)
        if(self._p1==None):
            self._t=[]
            return

        self._input_index=self._filter_index=self._output_index=None
        for i in xrange(len(self._t)):
            if self._t[i]=="input":
                self._input_index=i+1
            elif self._t[i]=="filter":
                self._filter_index=i+1
            elif self._t[i]=="output":
                self._output_index=i+1


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
    n=ni.NodeIdList("", ["send_to", "=", ">"], "(\w+)")
    nodeId["pipeline_output"]=n

    n=ni.NodeIdList("elastic", ["hosts", "=", ">"], "\"([^:]*):\d+\"")
    nodeId["elasticsearch_output"]=n

    n=ni.NodeIdMultipleFields("udp", [["port", "=", ">"], ["host", "=", ">", "\""]])
    nodeId["udp_output"]=n

    n=ni.NodeIdMultipleFields("tcp", [["port", "=", ">"], ["host", "=", ">", "\""]])
    nodeId["tcp_output"]=n

    n=ni.NodeIdSimple("stdout")
    nodeId["stdout_output"]=n


    # input identifiers
    n=ni.NodeIdSingleField("", ["address", "=", ">"])
    nodeId["pipeline_input"]=n

    n=ni.NodeIdSingleField("udp", ["port", "=", ">"])
    nodeId["udp_input"]=n

    n=ni.NodeIdSingleField("tcp", ["port", "=", ">"])
    nodeId["tcp_input"]=n

    n=ni.NodeIdSimple("stdin")
    nodeId["stdin_input"]=n

    n=ni.NodeIdSingleField("beats", ["port", "=", ">"])
    nodeId["beats_input"]=n


    # list of error to be printed (if verbose is True)
    # each element: (message, error type) 
    # Type: info, warning, error

    errors=[]

    with open(option.filename, "r") as stream:
        try:
            for p in (yaml.safe_load(stream)):
                try:
                    if 'config.string' in p.keys() and 'pipeline.id' in p.keys():
                        a=PipelineString(p['config.string'])
                    elif 'path.config' in p.keys() and 'pipeline.id' in p.keys():
                        a=PipelineFile(p['path.config'])

                    con[p['pipeline.id']]=(a.list_of_connections(nodeId, "input"), a.list_of_connections(nodeId, "output"))
                except Exception as e:
                    print e
                    errors.append((str(e), "error"))
                    node = Node(name=p['pipeline.id'], style="filled", shape="box", color="red", missingAllOutput=True, missingOutput=True, missingAllInput=True, missingInput=True)
                    nodes[p['pipeline.id']]=node
                    errors.append(("Pipeline %s cannot be parsed" % p['pipeline.id'], "error"))
                        
        except yaml.YAMLError as exc:
            print(exc)



    for n in con.keys():
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
            nodes[p].setMissingInput(True)
            errors.append(("Some of the input of pipeline %s are missing" % p, "info"))
        if(len(tmp_in)>0 and set(tmp_in).isdisjoint(tmp_out)==True): # missing all input
            nodes[p].setMissingAllInput(True)
            nodes[p].setColor("orange")
            nodes[p].setStyle("dashed")
            errors.append(("All the input of pipeline %s are missing (the pipeline is unused)" % p, "info"))

    tmp_in = [x[1] for p in con for x in con[p][0] if x[0]=="pipeline"]
    for p in con:
        tmp_out=[x[1] for x in con[p][1] if x[0]=="pipeline"] 
        if(set(tmp_out).issubset(tmp_in)==False): # missing an output
            nodes[p].setColor("red")
            nodes[p].setMissingOutput(True)
            errors.append(("Some of the output of pipeline %s are missing" % p, "error"))

        if(len(tmp_out)>0 and set(tmp_out).isdisjoint(tmp_in)==True): # missing all output
            nodes[p].setMissingAllOutput(True)
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
        for i in nodes[n].getOutgoingAdjacent():
            in_deg[i]+=1
    nodes_rank={}
    rank=0

    tmp_nodes=dict.copy(nodes)

    while(len(tmp_nodes)>0):
        # find sources (first we search for well connected nodes)
        flag=False
        for n in in_deg:
            if in_deg[n]==0 and tmp_nodes[n].getMissingAllInput()==False:
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
                for t in tmp_nodes[n].getOutgoingAdjacent():
                    in_deg[t]-=1
                del tmp_nodes[n]
                del in_deg[n]
        rank+=1

    g = Digraph(engine="dot", format='png')

    if(len(tmp_nodes)>0):  # cycles exists ! view it.
        # let's remove nodes in which their out degree is 0
        while(True):
            t = [n for n in tmp_nodes if len(tmp_nodes[n].isSink())==0]
            if(len(t)==0):
                break
            for i in t:
                del tmp_nodes[i]
                for v in tmp_nodes:
                    if i in tmp_nodes[v].getOutgoingAdjacent():
                        tmp_nodes[v].removeOutgoingAdjacent(i)


        tmp=dict.copy(tmp_nodes)
        for v in tmp_nodes:
            del tmp[v]
            if(hasCycle(tmp)==False):
                tmp[v]=tmp_nodes[v]
        
        
               
        for v in tmp:
            g.node(v, shape="box", style="filled", color="red")

        errors.append(("One or more cycles has been found", "error"))
        for v in tmp:
            for u in tmp[v].getOutgoingAdjacent():
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

                g.node(n, pos="%d,%d!" %(j, rank-i), shape=nodes[n].getShape(), style=nodes[n].getStyle(), color=nodes[n].getColor())
            
        for v in nodes:
            for u in nodes[v].getOutgoingAdjacent():
                g.edge(v, u)


        
    g.view()
    if(option.verbose==True):
        print_errors(errors)


if __name__=="__main__":
    main()
