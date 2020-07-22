from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import datetime


class UserQueryServiceConfigsTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/services/configs'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_auth(self):
        response = self._request_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_post_no_auth(self):
        response = self._post_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_delete_no_auth(self):
        response = self._delete_with_no_auth(id_to_del=0)
        self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 400)

    def test_query_combined_params_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_service=1&id_user=1'
                                                                                            '&id_participant=1')
        self.assertEqual(response.status_code, 400)
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_service=1&id_user=1'
                                                                                            '&id_device=1')
        self.assertEqual(response.status_code, 400)
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_service=1'
                                                                                            '&id_participant=1'
                                                                                            '&id_device=1')
        self.assertEqual(response.status_code, 400)

    def test_query_for_service_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_service=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_service'], 1)

    def test_query_for_user_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user'], 1)

    def test_query_for_device_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_device=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_device'], 1)

    def test_query_for_participant_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_participant=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_participant'], 1)

    def test_query_specific_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_service=1&id_user=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user'], 1)
            self.assertEqual(data_item['id_service'], 1)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_service=1&id_user=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_service=5&"
                                                                                            "id_participant=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_participant'], 1)
            self.assertEqual(data_item['id_service'], 5)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_service=3&"
                                                                                            "id_device=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_device'], 1)
            self.assertEqual(data_item['id_service'], 3)

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'service_config': {
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_service_config")  # Missing id_service_config

        json_data['service_config']['id_service_config'] = 0
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_service")

        json_data['service_config']['id_service'] = 1
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing at least one id")

        json_data['service_config']['id_user'] = 1
        response = self._post_with_http_auth(username='user3', password='user3', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        self._checkJson(json_data)
        current_id = json_data['id_service_config']

        json_data = {
            'service_config': {
                'id_service_config': current_id,
                'service_config_config': '{"Test"'
            }
        }
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Post update with invalid service_config_config schema")

        json_data['service_config']['service_config_config'] = '{"Globals": {"test_config": true}}'
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update OK")
        json_data = response.json()[0]
        self._checkJson(json_data)

        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_service_config'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('service_config_config'))
        self.assertTrue(json_data.__contains__('last_update_time'))
