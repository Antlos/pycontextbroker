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

    def test_create_entity(self):
        response = self.cbc.create_entity(
            "Search",
            "search_1",
            attributes=[{"name": "number", "type": "integer", "value": "0"}]
        )
        self.assertIsNotNone(response)
        self.assertIn('contextResponses', response)
        self.assertIn('type', response)
        self.assertEquals(response.get('type'), 'Search')
        self.assertIn('id', response)
        self.assertEquals(response.get('id'), 'search_1')
        self.assertIn('isPattern', response)
        self.assertEquals(response.get('isPattern'), 'false')

    def test_get_entity(self):
        response = self.cbc.get_entity("Search", "search_1")
        self.assertIsNotNone(response)
        self.assertIn('contextElement', response)
        self.assertIn('attributes', response.get('contextElement'))
        self.assertEquals('false', response.get('contextElement').get('isPattern'))
        self.assertEquals('search_1', response.get('contextElement').get('id'))
        self.assertEquals('Search', response.get('contextElement').get('type'))

    def test_get_attribute_value(self):
        if self.cbc.get_entity("Search", "search_1")['statusCode']['code'] == '404':
            self.cbc.create_entity("Search", "search_1", attributes=[{"name": "number", "type": "integer", "value": "0"}])
        response = self.cbc.get_attribute_value("Search", "search_1", "number")
        self.assertEquals('0', response)

    def test_update_attribute_value(self):
        self.cbc.update_attribute_value("Search", "search_1", "number", 1)
        self.assertEqual('1', self.cbc.get_attribute_value("Search", "search_1", "number"))

    def test_delete_entity(self):
        if self.cbc.get_entity("Search", "search_1")['statusCode']['code'] == '404':
            self.cbc.create_entity("Search", "search_1", attributes=[{"name": "number", "type": "integer", "value": "0"}])
        self.cbc.delete_entity("Search", "search_1")
        self.assertEquals(self.cbc.get_entity("Search", "search_1")['statusCode']['code'], '404')

    def test_subscribe_on_attribute_change(self):
        response = self.cbc.subscribe_on_attribute_change("Search", "search_1", "number", "http://localhost:3030/search_number")
        self.assertIn('subscribeResponse', response)
        self.assertIn('subscriptionId', response['subscribeResponse'])
        self.assertIn('throttling', response['subscribeResponse'])
        self.assertIn('duration', response['subscribeResponse'])

if __name__ == '__main__':
    unittest.main()
