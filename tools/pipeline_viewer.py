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
import getopt

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from graphviz import Digraph
import graphviz

class pipeline(object):
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
            (self.p1, self.p2) = pipeline.parenthesis(self.t)
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


    def list_of_inputs(self):
        x=self.get_input()
        (p1, p2) = pipeline.parenthesis(x)
        l=[]
        i=1
        
        while(i<len(x)):
            if x[i] in ["pipeline", "udp", "tcp", "stdin"]:
                l.append((x[i], i+1, p1[i+1]))
                i=p1[i+1]+1
            else:
                i+=1


        input_list=[]
        for i in l:
            if i[0]=='udp' or i[0]=="tcp":
                for j in xrange(i[1],i[2]):
                    if(x[j]=="port" and x[j+1]=="=" and x[j+2]==">"):
                        input_list.append((i[0], x[j+3]))
                        break
            if i[0]=='pipeline':
                for j in xrange(i[1],i[2]):
                    if(x[j]=="address" and x[j+1]=="=" and x[j+2]==">"):
                        input_list.append((i[0], x[j+3]))
                        break
                    
        return input_list


    def list_of_outputs(self):
        x=self.get_output()
        (p1, p2) = pipeline.parenthesis(x)
        l=[]
        i=1
        while(i<len(x)):
            if x[i] in ["pipeline", "udp, tcp", "elasticsearch", "stdout"]:
                l.append((x[i], i+1, p1[i+1]))
                i=p1[i+1]+1
            else:
                i+=1


        output_list=[]
        for i in l:
            if i[0]=='elasticsearch':
                for j in xrange(i[1], i[2]):
                    if(x[j]=="hosts" and x[j+1]=="=" and x[j+2]==">"):
                        k=0
                        while(x[j+3+k] != ']'):
                            if(x[j+4+k]==':'):
                                output_list.append((i[0], x[j+4+k-1]))
                            k+=1

            if i[0]=='stdout':
                output_list.append((i[0], i[0]))
            if i[0]=='udp' or i[0]=='tcp':
                output_list.append((i[0], i[0]))
            if i[0]=='udp' or i[0]=='tcp':
                output_list.append((i[0], i[0]))
            if i[0]=='pipeline':
                for j in xrange(i[1], i[2]):
                    if(x[j]=="send_to" and x[j+1]=="=" and x[j+2]==">" and x[j+3]=="["):
                        k=0
                        while(x[j+4+k] != ']'):
                            if(x[j+4+k]!=','):
                                output_list.append((i[0], x[j+4+k]))
                            k+=1
                        break
                    
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
        

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:")
    except getopt.GetoptError as err:
        print str(err)
        return 1

    filename=""
    for o, a in opts:
        if o=='-c':
            filename=a            # index suffix

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

    with open(filename, "r") as stream:
        try:
            for p in (yaml.safe_load(stream)):
                if 'path.config' in p.keys() and 'pipeline.id' in p.keys():
                    try:
                        a=pipeline(p['path.config'])
                        con[p['pipeline.id']]=(a.list_of_inputs(), a.list_of_outputs())
                    except:
                        node = Node(name=p['pipeline.id'], style="filled", shape="box", color="red", missingAllOutput=True, missingOutput=True, missingAllInput=True, missingInput=True)
                        nodes[p['pipeline.id']]=node
                        
        except yaml.YAMLError as exc:
            print "kuku"
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
                
            elif(a=='udp' or a=='tcp'):
                tmp=a+"-"+str(b)
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
            if(a=='elasticsearch'):
                tmp = "elastic" + "-" + b
                nodes[n].addOutgoingAdjacent(tmp)

                tmp_node=Node(name=tmp, style="filled", shape="ellipse", color="grey", missingAllOutput=False, missingAllInput=False)
                nodes[tmp]=tmp_node
            if(a=='stdout'):
                nodes[n].addOutgoingAdjacent(a)
                tmp_node=Node(name=a, style="filled", shape="ellipse", color="grey", missingAllOutput=False, missingAllInput=False)
                nodes[a]=tmp_node



    g = Digraph(engine="neato", format='png', graph_attr={'splines':"ortho"})
    tmp_out = [x[1] for p in con for x in con[p][1] if x[0]=="pipeline"]
    for p in con:
        tmp_in=[x[1] for x in con[p][0] if x[0]=="pipeline"] 
        if(set(tmp_in).issubset(tmp_out)==False): # missing an input
            nodes[p].setColor("orange")
            nodes[p].setMissigInput(True)
        if(len(tmp_in)>0 and set(tmp_in).isdisjoint(tmp_out)==True): # missing all input
            nodes[p].setMissigAllInput(True)
            nodes[p].setColor("orange")
            nodes[p].setStyle("dashed")        
    tmp_in = [x[1] for p in con for x in con[p][0] if x[0]=="pipeline"]
    for p in con:
        tmp_out=[x[1] for x in con[p][1] if x[0]=="pipeline"] 
        if(set(tmp_out).issubset(tmp_in)==False): # missing an output
            nodes[p].setColor("red")
            nodes[p].setMissigOutput(True)
        if(len(tmp_out)>0 and set(tmp_out).isdisjoint(tmp_in)==False): # missing all output
            nodes[p].setMissigAllOutput(True)

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
        # remove ranked nodes
        for n in nodes_rank:
            if nodes_rank[n]==rank:
                for t in tmp_nodes[n].outgoingAdjacent:
                    in_deg[t]-=1
                del tmp_nodes[n]
                del in_deg[n]
        rank+=1
         
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


main()
