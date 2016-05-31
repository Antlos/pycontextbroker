# pycontextbroker

## About

An opensource library that makes communications with Orion Context Broker smooth, easy and pythonic

## Dependencies

```
requests==2.9.1
```

## Installation

```
$ pip install pycontextbroker
```

## Examples

```python
from pycontextbroker.pycontextbroker import ContextBrokerClient

# Client
cbc = ContextBrokerClient('<your-context-broker-ip-address-here>', '<your-context-broker-port-here>')

version = cbc.get_version()  # "0.28.0-next"
up_time = cbc.get_uptime()  # "0 d, 23 h, 15 m, 9 s"

# Entities
cbc.entity.create("Entity", "IdOne")
cbc.entity.create("Entity", "IdTwo", attributes=[{"name": "number", "type": "integer", "value": "1"}])
cbc.entity.get("Entity", "IdTwo")  # {'contextElement': {'attributes': [{'value': '1', 'type': 'integer', 'name': 'number'}, {'value': '1', 'type': 'integer', 'name': 'number'}], 'isPattern': 'false', 'id': 'test_search_2', 'type': 'TestSearch'}, 'statusCode': {'code': '200', 'reasonPhrase': 'OK'}}

# Attributes
cbc.attribute.get("Entity", "IdTwo", "number")  # {'contextElement': {'isPattern': 'false', 'type': 'Entity', 'attributes': [{'type': 'integer', 'name': 'number', 'value': '1'}], 'id': 'IdTwo'}, 'statusCode': {'code': '200', 'reasonPhrase': 'OK'}}
cbc.attribute.get_value("Entity", "IdTwo", "number")  # "1"
cbc.attribute.update_value("Entity", "IdTwo", "number", 2)
cbc.attribute.get_value("Entity", "IdTwo", "number")  # "2"
cbc.attribute.create("Entity", "IdThree", "number", 100)
cbc.attribute.delete("Entity", "IdThree", "number")
cbc.attribute.get_value("Entity", "IdThree", "number")  # None

# Subscriptions
cbc.subscription.on_change("Entity", "IdTwo", "number", "<http://localhost:3030/i_am_listening_at_cb_here>")
cbc.subscription.all()  # [{'status': 'active', 'subject': {'entities': [{'type': 'TestSearch', 'idPattern': '', 'id': 'test_search_1'}], 'condition': {'expression': {'geometry': '', 'georel': '', 'coords': '', 'q': ''}, 'attributes': ['number']}}, 'expires': '2016-06-2...
cbc.subscription.unsubscribe('<subscription-id>')  # {'subscriptionId': '<subscription-id>', 'statusCode': {'code': '200', 'reasonPhrase': 'OK'}}
```

## References

https://github.com/telefonicaid/fiware-orion

http://www.slideshare.net/fermingalan/fiware-managing-context-information-at-large-scale
