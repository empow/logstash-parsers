# Multi Pipeline Viewer
The pipeline viewer read the Logstash pipeline.yml configuration file and all the Logstash configuration pipelines and view the connectivity map between these pipelines.

In addition, it marks configuration failures such as unused pipelines, unconnected input and output

![example](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_viewer.png)


## Instalation
The pipeline viewer  is a python script written in *python2*.
It relies on the following common *python2* packages:

1. yaml 
2. Queue
3. getopt
4. nltk
5. graphviz

The pipeline viewer can be run on any platform running *python2*. <br>
We will use *Ubuntu 18.04* as the reference platform for this note.

### Install *python2*
While *python2* is typically installed by default on *Ubuntu 18.04* you may installed it manually

```sh
sudo apt-get install python2.7
```


### install python packages
```sh
sudo pip install yaml Queue getopt nltk graphviz
```

## Usage
Once the required packages are installed the pipeline viewer can be executed as follow:

```sh
python2 pipeline_viewer.py -c <file name>
```

where *<file name\>* is the full path of your Logstash pipeline.yaml file (e.g. */etc/logstash/pipeline.yaml*)

The output is presened in a *png* format in contains the connectivity between pipelines including inputs and outputs. Thus, each pipeline is represented by a rectangle node while inputs and outputs are represented by ellipse nodes. In case that at least one of the output of a pipeline is not connected its corresponding node is

|||
|-|-|
|![pipeline_input](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_input.png) | A grey filled ellipse represents both input or output. |
|![pipeline_node](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_node.png) | A grey filled box represents a single pipeline that is determined in the *pipeline.yml* configuration file and its inputs and outputs are well connected.|
|![pipeline_red](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_node_red.png) | A red filled box represents a single pipeline that is determined in the *pipeline.yml* configuration file that either not exist or at leat one of its output pipeline does not exist.|
|![pipeline_orange](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_node_orange.png) | An orange filled box represents a single pipeline that is determined in the *pipeline.yml* configuration file in which at least one of its input pipeline is not determined.|
|![pipeline_dashed](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_node_dashed.png) | An orange dashed box represents a single pipeline that is determined in the *pipeline.yml* configuration file in which at all of its input are pipelines that are not determined (therefore the pipeline is unused and will process no packets).|
|![pipeline_dashed](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_multi.png) | A directed edge represent a connectivity between two pipelines.|


