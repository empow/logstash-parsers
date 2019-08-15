# logstash-parsers
```
- pipeline.id: single_port`
path.config: "<BASE_DIR>/logstash-parsers/virtual_input/single_port.conf"
- pipeline.id: elastic_output
```

path.config: "<BASE_DIR>/logstash-parsers/virtual_output/elastic_output.conf"
- pipeline.id: empow_classifier_output
path.config: "<BASE_DIR>/logstash-parsers/virtual_output/empow_classifier_output.conf"
- pipeline.id: default
path.config: "<BASE_DIR>/logstash-parsers/parsers/default_pipeline.conf"
- pipeline.id: snort
path.config: "<BASE_DIR>/logstash-parsers/parsers/snort/snort.conf"
- pipeline.id: fortinet
path.config: "<BASE_DIR>/logstash-parsers/parsers/fortinet/fortinet.conf"
- pipeline.id: cb
path.config: "<BASE_DIR>/logstash-parsers/parsers/carbonblack/cbdefense.conf"
- pipeline.id: symantec
path.config: "<BASE_DIR>/logstash-parsers/parsers/symantec/symantec.conf"

