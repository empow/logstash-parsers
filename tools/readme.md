# pipeline viewer


![pipeline_input](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_input.png) - A grey filled ellipse represents both input or output

![pipeline_node](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_node.png) - A grey filled box represents a single pipeline that is determined in the *pipeline.yml* configuration file and its inputs and outputs are well connected.

![pipeline_red](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_node_red.png) - A red filled box represents a single pipeline that is determined in the *pipeline.yml* configuration file that either not exist or at leat one of its output pipeline does not exist.

![pipeline_orange](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_node_orange.png) - An orange filled box represents a single pipeline that is determined in the *pipeline.yml* configuration file in which at least one of its input pipeline is not determined

![pipeline_dashed](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_node_dashed.png) - An orange dashed box represents a single pipeline that is determined in the *pipeline.yml* configuration file in which at all of its input are pipelines that are not determined (therefore the pipeline is unused and will process no packets)

![pipeline_dashed](https://github.com/empow/logstash-parsers/blob/master/tools/pipeline_multi.png] - A directed edge represent a connectivity between two pipelines
