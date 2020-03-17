import unittest
import os
from requests import get, post
import json


class DeviceQuerySessions(unittest.TestCase):

    host = 'localhost'
    port = 4040
    device_login_endpoint = '/api/device/login'
    device_logout_endpoint = '/api/device/logout'
    device_query_session_endpoint = '/api/device/sessions'
    device_query_session_events_endpoint = '/api/device/sessionevents'
    user_device_endpoint = '/api/user/devices'
    all_devices = None

    def setUp(self):
        # Use admin account to get device information (and tokens)
        response = self._http_auth_devices('admin', 'admin')
        self.assertEqual(response.status_code, 200)
        self.all_devices = json.loads(response.text)
        self.assertGreater(len(self.all_devices), 0)

    def tearDown(self):
        pass

    def _make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def _http_auth_devices(self, username, password):
        url = self._make_url(self.host, self.port, self.user_device_endpoint)
        return get(url=url, verify=False, auth=(username, password))

    def _token_auth(self, token):
        url = self._make_url(self.host, self.port, self.device_login_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def _token_auth_logout(self, token):
        url = self._make_url(self.host, self.port, self.device_logout_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def _token_auth_query_sessions_get(self, token):
        url = self._make_url(self.host, self.port, self.device_query_session_endpoint) + '?list=true'
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def _token_auth_query_sessions_post(self, token, session_info: dict = None):
        url = self._make_url(self.host, self.port, self.device_query_session_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return post(url=url, verify=False, json=session_info, headers=request_headers)

    def test_device_query_sessions_get(self):
        # Populate sessions for all devices
        for device in self.all_devices:
            if device['device_enabled']:
                response_sessions = self._token_auth_query_sessions_get(device['device_token'])
                self.assertEqual(response_sessions.status_code, 200)
                device['sessions'] = json.loads(response_sessions.text)
            else:
                response_sessions = self._token_auth_query_sessions_get(device['device_token'])
                self.assertEqual(response_sessions.status_code, 403)

    def test_device_query_sessions_post(self):
        # Populate sessions for all devices
        for device in self.all_devices:
            if device['device_enabled']:
                login_response = self._token_auth(device['device_token'])
                self.assertEqual(login_response.status_code, 200)
                device_info = login_response.json()
                # Get all participant ids
                participants_id_list = [participant['participant_uuid']
                                        for participant in device_info['participants_info']]

                # Invalid session
                session = {'session': {'id_session': 0, 'session_participants': participants_id_list}}

                session_response = self._token_auth_query_sessions_post(token=device['device_token'],
                                                                        session_info=session)

                self.assertEqual(session_response.status_code, 400)

                # Valid session
                session = {'session': {'id_session': 0,
                                       'session_participants': participants_id_list,
                                       'id_session_type': 2}}

                session_response = self._token_auth_query_sessions_post(token=device['device_token'],
                                                                        session_info=session)
                print(session_response.text)
                self.assertEqual(session_response.status_code, 200)
            else:
                login_response = self._token_auth(device['device_token'])
                self.assertEqual(login_response.status_code, 403)
