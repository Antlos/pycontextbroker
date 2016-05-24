from pycontextbroker.pycontextbroker import ContextBrokerClient
import unittest


class PycontextbrokerTestCase(unittest.TestCase):

    def setUp(self):
        self.cbc = ContextBrokerClient('192.168.99.100', '1026')

    def test_get_version_data(self):
        version_data = self.cbc.get_version_data()
        self.assertIsNotNone(version_data)
        self.assertIn('orion', version_data)

    def test_get_orion_version_data(self):
        orion_version_data = self.cbc.get_orion_version_data()
        self.assertIsNotNone(orion_version_data)
        self.assertIn('uptime', orion_version_data)
        self.assertIn('version', orion_version_data)

    def test_get_version(self):
        self.assertIsNotNone(self.cbc.get_version())

    def test_get_uptime(self):
        self.assertIsNotNone(self.cbc.get_uptime())

    # Entity
    def test_create_entity_without_attributes(self):
        response = self.cbc.entity.create(
            "TestSearch",
            "test_search_1",
        )
        self.assertIsNotNone(response)
        self.assertIn('contextResponses', response)
        self.assertNotIn('attributes', response.get('contextResponses')[0])
        self.assertIn('type', response)
        self.assertEquals(response.get('type'), 'TestSearch')
        self.assertIn('id', response)
        self.assertEquals(response.get('id'), 'test_search_1')
        self.assertIn('isPattern', response)
        self.assertEquals(response.get('isPattern'), 'false')

    def test_create_entity_with_attributes(self):
        response = self.cbc.entity.create(
            "TestSearch",
            "test_search_2",
            attributes=[{"name": "number", "type": "integer", "value": "1"}]
        )
        self.assertIsNotNone(response)
        self.assertIn('contextResponses', response)
        self.assertIn('attributes', response.get('contextResponses')[0])
        self.assertIn('type', response)
        self.assertEquals(response.get('type'), 'TestSearch')
        self.assertIn('id', response)
        self.assertEquals(response.get('id'), 'test_search_2')
        self.assertIn('isPattern', response)
        self.assertEquals(response.get('isPattern'), 'false')

    def test_get_entity_with_attribute(self):
        response = self.cbc.entity.get("TestSearch", "test_search_1")
        self.assertIsNotNone(response)
        self.assertIn('contextElement', response)
        self.assertIn('attributes', response.get('contextElement'))
        self.assertEquals('false', response.get('contextElement').get('isPattern'))
        self.assertEquals('test_search_1', response.get('contextElement').get('id'))
        self.assertEquals('TestSearch', response.get('contextElement').get('type'))

    def test_get_entitiy_without_attributes(self):
        response = self.cbc.entity.get("TestSearch", "test_search_2")
        self.assertIsNotNone(response)
        self.assertIn('contextElement', response)
        self.assertNotIn('attributes', response.get('contextElement'))
        self.assertEquals('false', response.get('contextElement').get('isPattern'))
        self.assertEquals('test_search_2', response.get('contextElement').get('id'))
        self.assertEquals('TestSearch', response.get('contextElement').get('type'))

    # Attributes
    def test_get_attribute_value(self):
        if self.cbc.entity.get("TestSearch", "test_search_1")['statusCode']['code'] == '404':
            self.cbc.entity.create("TestSearch", "test_search_1", attributes=[{"name": "number", "type": "integer", "value": "0"}])
        response = self.cbc.attribute.get_value("TestSearch", "test_search_1", "number")
        self.assertEquals('0', response)

    def test_update_attribute_value(self):
        self.cbc.attribute.update_value("TestSearch", "test_search_1", "number", 1)
        self.assertEqual('1', self.cbc.attribute.get_value("TestSearch", "test_search_1", "number"))

    def test_update_missing_attribute_value(self):
        self.cbc.attribute.update_value("TestSearch", "test_search_2", "number", 10)
        self.assertEqual('10', self.cbc.attribute.get_value("TestSearch", "test_search_2", "number"))

    def test_create_attribute(self):
        self.cbc.attribute.create("TestSearch", "test_search_2", "new_attribute", 33)
        self.assertEqual('33', self.cbc.attribute.get_value("TestSearch", "test_search_2", "new_attribute"))

    def test_delete_attribute_attribute_value(self):
        self.cbc.attribute.create("TestSearch", "test_search_2", "attribute_to_be_deleted", 66)
        self.assertEqual('66', self.cbc.attribute.get_value("TestSearch", "test_search_2", "attribute_to_be_deleted"))
        self.cbc.attribute.delete("TestSearch", "test_search_2", "attribute_to_be_deleted")
        self.assertIsNone(self.cbc.attribute.get_value("TestSearch", "test_search_2", "attribute_to_be_deleted"))

    def test_delete_entity(self):
        if self.cbc.entity.get("TestSearch", "test_search_1")['statusCode']['code'] == '404':
            self.cbc.entity.create("TestSearch", "test_search_1", attributes=[{"name": "number", "type": "integer", "value": "0"}])
        if self.cbc.entity.get("TestSearch", "test_search_2")['statusCode']['code'] == '404':
            self.cbc.entity.create("TestSearch", "test_search_2",
                                   attributes=[{"name": "number", "type": "integer", "value": "0"}])
        self.cbc.entity.delete("TestSearch", "test_search_1")
        self.assertEquals(self.cbc.entity.get("TestSearch", "test_search_1")['statusCode']['code'], '404')
        self.cbc.entity.delete("TestSearch", "test_search_2")
        self.assertEquals(self.cbc.entity.get("TestSearch", "test_search_2")['statusCode']['code'], '404')

    # Subscription
    def test_create_subscription_on_attribute_change(self):
        response = self.cbc.subscription.on_change("TestSearch", "test_search_1", "number", "http://localhost:3030/search_number")
        self.assertIn('subscribeResponse', response)
        self.assertIn('subscriptionId', response['subscribeResponse'])
        self.assertIn('throttling', response['subscribeResponse'])
        self.assertIn('duration', response['subscribeResponse'])

    def test_get_all_subscriptions(self):
        response = self.cbc.subscription.all()
        self.assertIsInstance(response, list)
        self.assertTrue(response)
        self.assertIn('status', response[0])
        self.assertIn('expires', response[0])
        self.assertIn('id', response[0])
        self.assertIn('subject', response[0])
        self.assertIn('entities', response[0].get('subject'))
        self.assertIn('type', response[0].get('subject').get('entities')[0])
        self.assertIn('id', response[0].get('subject').get('entities')[0])
        self.assertIn('condition', response[0].get('subject'))
        self.assertIn('attributes', response[0].get('subject').get('condition'))
        self.assertIn('notification', response[0])
        self.assertIn('callback', response[0].get('notification'))
        self.assertIn('attributes', response[0].get('notification'))

    def test_unsubscribe_no_subcription_with_such_id(self):
        response = self.cbc.subscription.unsubscribe("###")
        self.assertEqual(response.get('statusCode').get('code'), '400')
        self.assertEqual(response.get('statusCode').get('reasonPhrase'), 'Bad Request')

    def test_unsubscribe(self):
        subscriptions = self.cbc.subscription.all()
        initial_num_subsciptions = len(subscriptions)
        self.assertTrue(self.cbc.subscription.all())
        subscription_id = self.cbc.subscription.all()[0].get('id')
        self.assertIsNotNone(subscription_id)
        response = self.cbc.subscription.unsubscribe(subscription_id)
        self.assertEqual(response.get('subscriptionId'), subscription_id)
        self.assertIn('statusCode', response)
        self.assertEqual(response.get('statusCode').get('code'), '200')
        final_num_subscriptions = len(self.cbc.subscription.all())
        self.assertEqual(initial_num_subsciptions, final_num_subscriptions + 1)

if __name__ == '__main__':
    unittest.main()
