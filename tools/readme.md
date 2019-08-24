# Logstash Multi Pipeline Visualization
A utility for vizualizing Logstash [multi pipeline](https://www.elastic.co/guide/en/logstash/current/multiple-pipelines.html)  including [pipeline-to-pipeline](https://www.elastic.co/guide/en/logstash/current/pipeline-to-pipeline.html) configuration.The visualization helps in checking the correctness of the configuration and understand the data flow.

The Multi Pipeline Visualization reads the Logstash *pipeline.yml* configuration file and all related Logstash configuration pipelines and visualizes the connectivity map between the pipelines.

In addition, it marks configuration failures such as unused pipelines, and unconnected input and output.

![example](https://github.com/empow/logstash-parsers/blob/master/images/pipeline_viewer.png)


## Instalation
The Multi Pipeline Visualization  is a python script written in *python2*.
It relies on the following common *python2* packages:

1. yaml 
2. Queue
3. getopt
4. nltk
5. graphviz

The utilityr can be run on any platform running *python2*. <br>
We will use *Ubuntu 18.04* as the reference platform for this note.

### Install *python2*
While *python2* is typically installed by default on *Ubuntu 18.04* you may install it manually

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

The output is presented in *png* format and shows the connectivity between pipelines including inputs and outputs. Each pipeline is represented by a rectangle node while inputs and outputs are represented by ellipse nodes.


|||
|-|-|
|![pipeline_input](https://github.com/empow/logstash-parsers/blob/master/images/pipeline_input.png) | A grey filled ellipse represents both input or output. |
|![pipeline_node](https://github.com/empow/logstash-parsers/blob/master/images/pipeline_node.png) | A grey filled box represents a single pipeline that is determined in the *pipeline.yml* configuration file and its inputs and outputs are well connected.|
|![pipeline_red](https://github.com/empow/logstash-parsers/blob/master/images/pipeline_node_red.png) | A red filled box represents a single pipeline that is determined in the *pipeline.yml* configuration file that either not exist or at leat one of its output pipeline does not exist.|
|![pipeline_orange](https://github.com/empow/logstash-parsers/blob/master/images/pipeline_node_orange.png) | An orange filled box represents a single pipeline that is determined in the *pipeline.yml* configuration file in which at least one of its input pipeline is not determined.|
|![pipeline_dashed](https://github.com/empow/logstash-parsers/blob/master/images/pipeline_node_dashed.png) | An orange dashed box represents a single pipeline that is determined in the *pipeline.yml* configuration file in which at all of its input are pipelines that are not determined (therefore the pipeline is unused and will process no packets).|
|![pipeline_multi](https://github.com/empow/logstash-parsers/blob/master/images/pipeline_multi.png) | A directed edge represent a connectivity between two pipelines.|
|![pipeline_cycle](https://github.com/empow/logstash-parsers/blob/master/images/pipeline_cycle.png)|A directed red cycle represent a cycle between pipelines|


