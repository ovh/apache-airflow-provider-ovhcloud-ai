# SPDX-License-Identifier: Apache-2.0
from unittest import mock
import pytest
from apache_airflow_provider_ovhcloud_ai.hooks.ai_training import OVHCloudAITrainingHook


class DummyConnection:
    def __init__(self, password=None, login=None):
        self.password = password
        self.login = login


def test_get_conn_uses_password():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="my-secret-token", login="bhs")
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        assert hook.get_conn() == "my-secret-token"


def test_get_conn_invalid_region():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="token", login="invalid")
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        with pytest.raises(Exception) as exc_info:
            hook.get_conn()
        assert "Invalid region" in str(exc_info.value)


def test_get_headers():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="header-token", login="bhs")
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        headers = hook._get_headers()
        assert headers == {
            "Authorization": "Bearer header-token",
            "Content-Type": "application/json",
        }


def test_submit_job_calls_make_request():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="token", login="bhs")
    expected_response = {"id": "job-123", "status": {"state": "PENDING"}}
    
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        with mock.patch.object(hook, "_make_request", return_value=expected_response) as mock_make:
            resp = hook.submit_job(
                image="pytorch/pytorch:latest",
                name="test-job",
                gpu=1,
                command=["python", "train.py"],
            )
            
            mock_make.assert_called_once()
            call_args = mock_make.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "v1/job"
            
            data = call_args[1]["data"]
            assert data["image"] == "pytorch/pytorch:latest"
            assert data["name"] == "test-job"
            assert data["resources"]["gpu"] == 1
            assert data["command"] == ["python", "train.py"]
            
            assert resp == expected_response


def test_submit_job_with_flavor():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="token", login="bhs")
    expected_response = {"id": "job-456", "status": {"state": "PENDING"}}
    
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        with mock.patch.object(hook, "_make_request", return_value=expected_response) as mock_make:
            resp = hook.submit_job(
                image="pytorch/pytorch:latest",
                flavor="ai1-1-gpu",
            )
            
            data = mock_make.call_args[1]["data"]
            assert data["resources"]["flavor"] == "ai1-1-gpu"
            assert resp == expected_response


def test_build_volume():
    volume = OVHCloudAITrainingHook.build_volume(
        container="my-container",
        alias="my-alias",
        mount_path="/workspace/data",
        permission="RW",
        cache=True,
    )
    
    assert volume["volumeSource"]["dataStore"]["container"] == "my-container"
    assert volume["volumeSource"]["dataStore"]["alias"] == "my-alias"
    assert volume["mountPath"] == "/workspace/data"
    assert volume["permission"] == "RW"
    assert volume["cache"] is True


def test_build_env_vars():
    env_vars = OVHCloudAITrainingHook.build_env_vars({
        "EPOCHS": "100",
        "LEARNING_RATE": "0.001",
    })
    
    assert len(env_vars) == 2
    assert {"name": "EPOCHS", "value": "100"} in env_vars
    assert {"name": "LEARNING_RATE", "value": "0.001"} in env_vars


def test_get_job():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="token", login="bhs")
    expected_response = {"id": "job-123", "status": {"state": "RUNNING"}}
    
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        with mock.patch.object(hook, "_make_request", return_value=expected_response) as mock_make:
            resp = hook.get_job("job-123")
            mock_make.assert_called_once_with("GET", "v1/job/job-123")
            assert resp == expected_response


def test_get_job_status():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="token", login="bhs")
    job_response = {"id": "job-123", "status": {"state": "DONE"}}
    
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        with mock.patch.object(hook, "_make_request", return_value=job_response):
            status = hook.get_job_status("job-123")
            assert status == "DONE"


def test_list_jobs():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="token", login="bhs")
    expected_response = {"items": [{"id": "job-1"}, {"id": "job-2"}]}
    
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        with mock.patch.object(hook, "_make_request", return_value=expected_response) as mock_make:
            resp = hook.list_jobs(page=1, size=50, state="RUNNING")
            mock_make.assert_called_once_with(
                "GET", "v1/job", params={"page": 1, "size": 50, "state": "RUNNING"}
            )
            assert resp == expected_response


def test_stop_job():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="token", login="bhs")
    
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        with mock.patch.object(hook, "_make_request", return_value={}) as mock_make:
            hook.stop_job("job-123")
            mock_make.assert_called_once_with("PUT", "v1/job/job-123/kill")


def test_delete_job():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="token", login="bhs")
    
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        with mock.patch.object(hook, "_make_request", return_value={}) as mock_make:
            hook.delete_job("job-123")
            mock_make.assert_called_once_with("DELETE", "v1/job/job-123")


def test_get_job_logs():
    hook = OVHCloudAITrainingHook()
    dummy_conn = DummyConnection(password="token", login="bhs")
    log_response = """
    2002-02-01T00:50:47Z [ovh] Job status is now INITIALIZING : JOB_INITIALIZING : Pulling job's data
    2002-02-01T00:50:53Z [ovh] Job status is now PENDING : JOB_PENDING : Pulling job's image
    """
    
    with mock.patch.object(hook, "get_connection", return_value=dummy_conn):
        with mock.patch.object(hook, "_make_request", return_value=log_response) as mock_make:
            logs = hook.get_job_logs("job-123", tail=100)
            mock_make.assert_called_once_with(
                "GET", "v1/job/job-123/log", params={"tail": 100}
            )
            assert logs == log_response


def test_region_urls():
    assert OVHCloudAITrainingHook.REGIONS["gra"] == "https://gra.ai.cloud.ovh.net"
    assert OVHCloudAITrainingHook.REGIONS["bhs"] == "https://bhs.ai.cloud.ovh.net"

