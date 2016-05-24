import json
import logging
import requests

logger = logging.getLogger(__name__)


class ContextBrokerEntity(object):
    def __init__(self, cb_address):
        self.cb_entities_api = cb_address + '/v1/contextEntities'

    def create(self, entity_type, entity_id, attributes=None):
        data = {
            "id": entity_id,
            "type": entity_type
        }

        if attributes:
            # [{"name": "number", "type": "integer", "value": "0"}]
            data.update({"attributes": attributes})

        return requests.post(
            self.cb_entities_api,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        ).json()

    # Read
    def get(self, entity_type, entity_id):
        endpoint = '/type/{}/id/{}'.format(entity_type, entity_id)
        return requests.get(self.cb_entities_api + endpoint).json()

    # Delete
    def delete(self, entity_type, entity_id):
        endpoint = '/type/{}/id/{}'.format(entity_type, entity_id)
        return requests.delete(self.cb_entities_api + endpoint).json()


class ContextBrokerAttribute(object):
    def __init__(self, cb_address):
        self.cb_entities_api = cb_address + '/v1/contextEntities'
        self.entity = ContextBrokerEntity(cb_address)

    def get_value(self, entity_type, entity_id, attribute_name):
        if self.entity.get(entity_type, entity_id).get('contextElement') is None:
            return None
        if self.entity.get(entity_type, entity_id).get('contextElement').get('attributes') is None:
            return None
        for attribute in self.entity.get(entity_type, entity_id).get('contextElement').get('attributes'):
            if attribute['name'] == attribute_name:
                return attribute.get('value')
        return None

    def create(self, entity_type, entity_id, attribute_name, attribute_value):
        if self.get_value(entity_type, entity_id, attribute_name) is not None:
            return None

        endpoint = '/type/{}/id/{}'.format(entity_type, entity_id)
        data = {
            "attributes": [
                {
                    "name": attribute_name,
                    "type": "integer",
                    "value": attribute_value
                }
            ]
        }
        return requests.post(
            self.cb_entities_api + endpoint,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        ).json()

    def update_value(self, entity_type, entity_id, attribute_name, attribute_value):
        # create attribute if it was never created
        if self.get_value(entity_type, entity_id, attribute_name) is None:
            return self.create(entity_type, entity_id, attribute_name, attribute_value)

        data = {"value": attribute_value}
        endpoint = '/type/{}/id/{}/attributes/{}'.format(entity_type, entity_id, attribute_name)
        return requests.put(self.cb_entities_api + endpoint,
                            data=json.dumps(data),
                            headers={'Content-Type': 'application/json'}).json()

    def delete(self, entity_type, entity_id, attribute_name):
        endpoint = '/type/{}/id/{}/attributes/{}'.format(entity_type, entity_id, attribute_name)
        return requests.delete(self.cb_entities_api + endpoint,
                               headers={'Content-Type': 'application/json'}).json()


class ContextBrokerSubscription(object):
    def __init__(self, cb_address):
        self.cb_subscription_api = cb_address + '/v1/subscribeContext'
        self.cb_subscription_v2_api = cb_address + '/v2/subscriptions'
        self.cb_unsubscription_api = cb_address + '/v1/unsubscribeContext'

    def all(self):
        return requests.get(self.cb_subscription_v2_api).json()

    def on_change(self, entity_type, entity_id, attribute_name, subscriber_endpoint):
        subscription_data = {
            "entities": [
                {
                    "type": entity_type,
                    "isPattern": "false",
                    "id": entity_id
                }
            ],
            "attributes": [
                attribute_name
            ],
            "reference": subscriber_endpoint,
            "duration": "P1M",
            "notifyConditions": [
                {
                    "type": "ONCHANGE",
                    "condValues": [
                        attribute_name
                    ]
                }
            ],
            "throttling": "PT5S"
        }

        return requests.post(self.cb_subscription_api,
                             data=json.dumps(subscription_data),
                             headers={'Content-Type': 'application/json'}).json()

    def unsubscribe(self, subscription_id):
        data = {
            "subscriptionId": subscription_id
        }
        return requests.post(self.cb_unsubscription_api,
                             data=json.dumps(data),
                             headers={'Content-Type': 'application/json'}).json()


class ContextBrokerClient(object):

    def __init__(self, ip, port):
        self.cb_address = 'http://{}:{}'.format(ip, port)
        self.entity = ContextBrokerEntity(self.cb_address)
        self.attribute = ContextBrokerAttribute(self.cb_address)
        self.subscription = ContextBrokerSubscription(self.cb_address)

        try:
            requests.get(self.cb_address)
        except:
            logger.exception("Failed to initialize ContextBroker client: "
                             "connection refused, please check provided IP and PORT")

    # Context Broker
    def get_version_data(self):
        return requests.get(self.cb_address + '/version').json()

    def get_orion_version_data(self):
        orion_data = self.get_version_data().get('orion')
        if not orion_data:
            logger.exception("Failed to gather Orion Context Broker version data")
        return orion_data

    def get_version(self):
        return self.get_orion_version_data().get('version')

    def get_uptime(self):
        return self.get_orion_version_data().get('uptime')
