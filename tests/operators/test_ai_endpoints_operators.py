# SPDX-License-Identifier: Apache-2.0
import pytest
from unittest.mock import patch, MagicMock
from apache_airflow_provider_ovhcloud_ai.operators.ai_endpoints import OVHCloudAIEndpointsChatCompletionsOperator

@pytest.fixture
def operator():
    return OVHCloudAIEndpointsChatCompletionsOperator(
        task_id="chat_completion_test",
        model="gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ],
        temperature=0.7,
        max_tokens=50,
        top_p=0.9,
        stop=None,
        stream=True,
    )

@patch("apache_airflow_provider_ovhcloud_ai.operators.ai_endpoints.OVHCloudAIEndpointsHook")
def test_execute_calls_chat_completion(mock_hook_class, operator):
    mock_hook = MagicMock()
    mock_hook.chat_completion.return_value = {
        "id": "cmpl-123",
        "object": "chat.completion",
        "choices": [{"message": {"role": "assistant", "content": "Hello!"}}],
        "usage": {"total_tokens": 42}
    }
    mock_hook_class.return_value = mock_hook

    result = operator.execute(context={})

    mock_hook_class.assert_called_once_with(ovh_conn_id=operator.ovh_conn_id)
    mock_hook.chat_completion.assert_called_once_with(
        model="gpt-oss-120b",
        messages=operator.messages,
        temperature=0.7,
        max_tokens=50,
        top_p=0.9,
        stream=True,
        stop=None,
    )
    assert result["id"] == "cmpl-123"
    assert result["usage"]["total_tokens"] == 42
