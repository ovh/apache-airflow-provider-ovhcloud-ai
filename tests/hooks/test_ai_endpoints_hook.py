from unittest import mock
from apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints import OVHCloudAIEndpointsHook


class DummyConnection:
    def __init__(self, password=None, extra=None):
        self.password = password
        self._extra = extra or {}

    def get_extra(self):
        return self._extra


def test_get_conn_uses_password():
    hook = OVHCloudAIEndpointsHook()
    dummy_conn = DummyConnection(password="my-secret-key")
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        assert hook.get_conn() == "my-secret-key"


def test_get_conn_uses_extra_key():
    hook = OVHCloudAIEndpointsHook()
    dummy_conn = DummyConnection(password=None, extra={"api_key": "extra-key"})
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        assert hook.get_conn() == "extra-key"


def test_get_headers():
    hook = OVHCloudAIEndpointsHook()
    dummy_conn = DummyConnection(password="header-key")
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        headers = hook._get_headers()
        assert headers == {
            "Authorization": "Bearer header-key",
            "Content-Type": "application/json",
        }


def test_chat_completion_calls_make_request():
    hook = OVHCloudAIEndpointsHook()
    dummy_conn = DummyConnection(password="token")
    expected_response = {"choices": []}
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        with mock.patch.object(hook, "_make_request", return_value=expected_response) as mock_make:
            resp = hook.chat_completion(
                model="test-model",
                messages=[{"role": "user", "content": "hi"}],
                temperature=0.5,
            )
            mock_make.assert_called_once_with(
                "POST",
                "chat/completions",
                {
                    "model": "test-model",
                    "messages": [{"role": "user", "content": "hi"}],
                    "temperature": 0.5,
                    "stream": False,
                },
            )
            assert resp == expected_response