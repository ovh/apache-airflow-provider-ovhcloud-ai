# SPDX-License-Identifier: Apache-2.0
import pytest
from unittest.mock import patch, MagicMock
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingSubmitJobOperator,
    OVHCloudAITrainingGetJobOperator,
    OVHCloudAITrainingStopJobOperator,
    OVHCloudAITrainingDeleteJobOperator,
    OVHCloudAITrainingGetLogsOperator,
    OVHCloudAITrainingWaitForJobOperator,
)


@pytest.fixture
def submit_operator():
    return OVHCloudAITrainingSubmitJobOperator(
        task_id="submit_job_test",
        image="pytorch/pytorch:latest",
        name="test-training-job",
        command=["python", "train.py"],
        flavor="ai1-1-gpu",
        env_vars={"EPOCHS": "10"},
        wait_for_completion=False,
    )


@pytest.fixture
def submit_operator_with_wait():
    return OVHCloudAITrainingSubmitJobOperator(
        task_id="submit_job_wait_test",
        image="pytorch/pytorch:latest",
        name="test-training-job",
        gpu=1,
        wait_for_completion=True,
        check_interval=5,
        wait_timeout=60,
    )


@patch("apache_airflow_provider_ovhcloud_ai.operators.ai_training.OVHCloudAITrainingHook")
def test_submit_job_execute(mock_hook_class, submit_operator):
    mock_hook = MagicMock()
    mock_hook.submit_job.return_value = {
        "id": "job-123",
        "status": {"state": "PENDING"},
    }
    # Mock the static method
    mock_hook_class.build_env_vars = MagicMock(return_value=[{"name": "EPOCHS", "value": "10"}])
    mock_hook_class.return_value = mock_hook

    result = submit_operator.execute(context={})

    mock_hook_class.assert_called_once_with(
        ovh_conn_id=submit_operator.ovh_conn_id,
        region=None,
    )
    mock_hook.submit_job.assert_called_once_with(
        image="pytorch/pytorch:latest",
        name="test-training-job",
        command=["python", "train.py"],
        env_vars=[{"name": "EPOCHS", "value": "10"}],
        gpu=0,
        gpu_model=None,
        cpu=None,
        flavor="ai1-1-gpu",
        volumes=None,
        labels=None,
        ssh_public_keys=None,
        default_http_port=None,
        timeout=None,
        unsecure_http=False,
    )
    assert result["id"] == "job-123"


@patch("apache_airflow_provider_ovhcloud_ai.operators.ai_training.OVHCloudAITrainingHook")
def test_submit_job_with_wait(mock_hook_class, submit_operator_with_wait):
    mock_hook = MagicMock()
    mock_hook.submit_job.return_value = {
        "id": "job-456",
        "status": {"state": "PENDING"},
    }
    mock_hook.wait_for_job.return_value = {
        "id": "job-456",
        "status": {"state": "DONE"},
    }
    mock_hook_class.return_value = mock_hook

    result = submit_operator_with_wait.execute(context={})

    mock_hook.wait_for_job.assert_called_once_with(
        job_id="job-456",
        check_interval=5,
        timeout=60,  # This is wait_timeout
    )
    assert result["status"]["state"] == "DONE"


@patch("apache_airflow_provider_ovhcloud_ai.operators.ai_training.OVHCloudAITrainingHook")
def test_get_job_execute(mock_hook_class):
    operator = OVHCloudAITrainingGetJobOperator(
        task_id="get_job_test",
        job_id="job-123",
    )
    
    mock_hook = MagicMock()
    mock_hook.get_job.return_value = {
        "id": "job-123",
        "status": {"state": "RUNNING"},
    }
    mock_hook_class.return_value = mock_hook

    result = operator.execute(context={})

    mock_hook.get_job.assert_called_once_with("job-123")
    assert result["id"] == "job-123"
    assert result["status"]["state"] == "RUNNING"


@patch("apache_airflow_provider_ovhcloud_ai.operators.ai_training.OVHCloudAITrainingHook")
def test_stop_job_execute(mock_hook_class):
    operator = OVHCloudAITrainingStopJobOperator(
        task_id="stop_job_test",
        job_id="job-123",
    )
    
    mock_hook = MagicMock()
    mock_hook.stop_job.return_value = {}
    mock_hook_class.return_value = mock_hook

    operator.execute(context={})

    mock_hook.stop_job.assert_called_once_with("job-123")


@patch("apache_airflow_provider_ovhcloud_ai.operators.ai_training.OVHCloudAITrainingHook")
def test_delete_job_execute(mock_hook_class):
    operator = OVHCloudAITrainingDeleteJobOperator(
        task_id="delete_job_test",
        job_id="job-123",
    )
    
    mock_hook = MagicMock()
    mock_hook.delete_job.return_value = {}
    mock_hook_class.return_value = mock_hook

    operator.execute(context={})

    mock_hook.delete_job.assert_called_once_with("job-123")


@patch("apache_airflow_provider_ovhcloud_ai.operators.ai_training.OVHCloudAITrainingHook")
def test_get_logs_execute(mock_hook_class):
    operator = OVHCloudAITrainingGetLogsOperator(
        task_id="get_logs_test",
        job_id="job-123",
        tail=50,
    )
    
    mock_hook = MagicMock()
    mock_hook.get_job_logs.return_value = "Log line 1\nLog line 2"
    mock_hook_class.return_value = mock_hook

    result = operator.execute(context={})

    mock_hook.get_job_logs.assert_called_once_with("job-123", tail=50)
    assert result == "Log line 1\nLog line 2"


@patch("apache_airflow_provider_ovhcloud_ai.operators.ai_training.OVHCloudAITrainingHook")
def test_wait_for_job_execute(mock_hook_class):
    operator = OVHCloudAITrainingWaitForJobOperator(
        task_id="wait_job_test",
        job_id="job-123",
        target_states=["DONE", "COMPLETED"],
        check_interval=10,
        timeout=300,
    )
    
    mock_hook = MagicMock()
    mock_hook.wait_for_job.return_value = {
        "id": "job-123",
        "status": {"state": "DONE"},
    }
    mock_hook_class.return_value = mock_hook

    result = operator.execute(context={})

    mock_hook.wait_for_job.assert_called_once_with(
        job_id="job-123",
        target_states=["DONE", "COMPLETED"],
        failure_states=None,
        check_interval=10,
        timeout=300,
    )
    assert result["status"]["state"] == "DONE"


def test_template_fields():
    """Test that template fields are correctly defined."""
    assert "image" in OVHCloudAITrainingSubmitJobOperator.template_fields
    assert "name" in OVHCloudAITrainingSubmitJobOperator.template_fields
    assert "command" in OVHCloudAITrainingSubmitJobOperator.template_fields
    assert "job_id" in OVHCloudAITrainingGetJobOperator.template_fields
    assert "job_id" in OVHCloudAITrainingStopJobOperator.template_fields
    assert "job_id" in OVHCloudAITrainingDeleteJobOperator.template_fields
    assert "job_id" in OVHCloudAITrainingGetLogsOperator.template_fields
    assert "job_id" in OVHCloudAITrainingWaitForJobOperator.template_fields

