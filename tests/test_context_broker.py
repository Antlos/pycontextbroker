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

    def test_create_entity_without_attributes(self):
        response = self.cbc.create_entity(
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
        response = self.cbc.create_entity(
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
        response = self.cbc.get_entity("TestSearch", "test_search_1")
        self.assertIsNotNone(response)
        self.assertIn('contextElement', response)
        self.assertIn('attributes', response.get('contextElement'))
        self.assertEquals('false', response.get('contextElement').get('isPattern'))
        self.assertEquals('test_search_1', response.get('contextElement').get('id'))
        self.assertEquals('TestSearch', response.get('contextElement').get('type'))

    def test_get_entitiy_without_attributes(self):
        response = self.cbc.get_entity("TestSearch", "test_search_2")
        self.assertIsNotNone(response)
        self.assertIn('contextElement', response)
        self.assertNotIn('attributes', response.get('contextElement'))
        self.assertEquals('false', response.get('contextElement').get('isPattern'))
        self.assertEquals('test_search_2', response.get('contextElement').get('id'))
        self.assertEquals('TestSearch', response.get('contextElement').get('type'))

    def test_get_attribute_value(self):
        if self.cbc.get_entity("TestSearch", "test_search_1")['statusCode']['code'] == '404':
            self.cbc.create_entity("TestSearch", "test_search_1", attributes=[{"name": "number", "type": "integer", "value": "0"}])
        response = self.cbc.get_attribute_value("TestSearch", "test_search_1", "number")
        self.assertEquals('0', response)

    def test_update_attribute_value(self):
        self.cbc.update_attribute_value("TestSearch", "test_search_1", "number", 1)
        self.assertEqual('1', self.cbc.get_attribute_value("TestSearch", "test_search_1", "number"))

    def test_update_missing_attribute_value(self):
        self.cbc.update_attribute_value("TestSearch", "test_search_2", "number", 10)
        self.assertEqual('10', self.cbc.get_attribute_value("TestSearch", "test_search_2", "number"))

    def test_create_attribute(self):
        self.cbc.create_attribute("TestSearch", "test_search_2", "new_attribute", 33)
        self.assertEqual('33', self.cbc.get_attribute_value("TestSearch", "test_search_2", "new_attribute"))

    def test_delete_attribute_attribute_value(self):
        self.cbc.create_attribute("TestSearch", "test_search_2", "attribute_to_be_deleted", 66)
        self.assertEqual('66', self.cbc.get_attribute_value("TestSearch", "test_search_2", "attribute_to_be_deleted"))
        self.cbc.delete_attribute("TestSearch", "test_search_2", "attribute_to_be_deleted")
        self.assertIsNone(self.cbc.get_attribute_value("TestSearch", "test_search_2", "attribute_to_be_deleted"))

    def test_delete_entity(self):
        if self.cbc.get_entity("TestSearch", "test_search_1")['statusCode']['code'] == '404':
            self.cbc.create_entity("TestSearch", "test_search_1", attributes=[{"name": "number", "type": "integer", "value": "0"}])
        if self.cbc.get_entity("TestSearch", "test_search_2")['statusCode']['code'] == '404':
            self.cbc.create_entity("TestSearch", "test_search_2",
                                   attributes=[{"name": "number", "type": "integer", "value": "0"}])
        self.cbc.delete_entity("TestSearch", "test_search_1")
        self.assertEquals(self.cbc.get_entity("TestSearch", "test_search_1")['statusCode']['code'], '404')
        self.cbc.delete_entity("TestSearch", "test_search_2")
        self.assertEquals(self.cbc.get_entity("TestSearch", "test_search_2")['statusCode']['code'], '404')

    def test_subscribe_on_attribute_change(self):
        response = self.cbc.subscribe_on_attribute_change("TestSearch", "test_search_1", "number", "http://localhost:3030/search_number")
        self.assertIn('subscribeResponse', response)
        self.assertIn('subscriptionId', response['subscribeResponse'])
        self.assertIn('throttling', response['subscribeResponse'])
        self.assertIn('duration', response['subscribeResponse'])

if __name__ == '__main__':
    unittest.main()
