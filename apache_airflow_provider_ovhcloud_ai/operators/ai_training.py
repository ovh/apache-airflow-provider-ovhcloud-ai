# SPDX-License-Identifier: Apache-2.0
from typing import Any, Dict, List, Optional
from airflow.models import BaseOperator
from apache_airflow_provider_ovhcloud_ai.hooks.ai_training import OVHCloudAITrainingHook


class OVHCloudAITrainingSubmitJobOperator(BaseOperator):
    """
    Operator to submit an AI Training job on OVHcloud.
    
    See API spec: https://bhs.ai.cloud.ovh.net/#/operations/jobNew
    
    :param image: Docker image to use for the job
    :param ovh_conn_id: Connection ID for OVHcloud AI Training
    :param region: OVHcloud region (gra or bhs)
    :param name: Optional name for the job
    :param command: Command to execute in the container
    :param env_vars: Environment variables (dict {"KEY": "value"} or list [{"name": "KEY", "value": "value"}])
    :param gpu: Number of GPUs to allocate
    :param gpu_model: GPU model to use (e.g., "V100S", "A100")
    :param cpu: Number of CPUs to allocate
    :param flavor: Specific flavor/instance type to use (e.g., "ai1-1-gpu")
    :param volumes: List of volume configurations to mount
    :param labels: Labels to attach to the job
    :param ssh_public_keys: SSH public keys for remote access
    :param default_http_port: Default HTTP port exposed by the job
    :param job_timeout: Job timeout in seconds
    :param unsecure_http: Allow unsecure HTTP access
    :param wait_for_completion: Whether to wait for job completion
    :param check_interval: Seconds between status checks when waiting
    :param wait_timeout: Maximum seconds to wait for completion
    
    Example:
        .. code-block:: python
        
            submit_job = OVHCloudAITrainingSubmitJobOperator(
                task_id='submit_training_job',
                image='pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime',
                name='my-training-job',
                command=['python', 'train.py'],
                flavor='ai1-1-gpu',
                env_vars={"EPOCHS": "100", "BATCH_SIZE": "32"},
                volumes=[
                    OVHCloudAITrainingHook.build_volume(
                        container="training-data",
                        mount_path="/workspace/data",
                        permission="RO",
                    )
                ],
                wait_for_completion=True,
            )
    """
    
    template_fields = ("image", "name", "command", "env_vars", "labels")
    
    def __init__(
        self,
        image: str,
        ovh_conn_id: str = OVHCloudAITrainingHook.default_conn_name,
        region: Optional[str] = None,
        name: Optional[str] = None,
        command: Optional[List[str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        gpu: int = 0,
        gpu_model: Optional[str] = None,
        cpu: Optional[int] = None,
        flavor: Optional[str] = None,
        volumes: Optional[List[Dict[str, Any]]] = None,
        labels: Optional[Dict[str, str]] = None,
        ssh_public_keys: Optional[List[str]] = None,
        default_http_port: Optional[int] = None,
        job_timeout: Optional[int] = None,
        unsecure_http: bool = False,
        wait_for_completion: bool = False,
        check_interval: int = 30,
        wait_timeout: int = 3600,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.image = image
        self.ovh_conn_id = ovh_conn_id
        self.region = region
        self.name = name
        self.command = command
        self.env_vars = env_vars
        self.gpu = gpu
        self.gpu_model = gpu_model
        self.cpu = cpu
        self.flavor = flavor
        self.volumes = volumes
        self.labels = labels
        self.ssh_public_keys = ssh_public_keys
        self.default_http_port = default_http_port
        self.job_timeout = job_timeout
        self.unsecure_http = unsecure_http
        self.wait_for_completion = wait_for_completion
        self.check_interval = check_interval
        self.wait_timeout = wait_timeout
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the job submission."""
        hook = OVHCloudAITrainingHook(
            ovh_conn_id=self.ovh_conn_id,
            region=self.region,
        )
        
        # Convert env_vars dict to list format if needed
        env_vars_list = None
        if self.env_vars:
            if isinstance(self.env_vars, dict):
                env_vars_list = OVHCloudAITrainingHook.build_env_vars(self.env_vars)
            else:
                env_vars_list = self.env_vars
        
        response = hook.submit_job(
            image=self.image,
            name=self.name,
            command=self.command,
            env_vars=env_vars_list,
            gpu=self.gpu,
            gpu_model=self.gpu_model,
            cpu=self.cpu,
            flavor=self.flavor,
            volumes=self.volumes,
            labels=self.labels,
            ssh_public_keys=self.ssh_public_keys,
            default_http_port=self.default_http_port,
            timeout=self.job_timeout,
            unsecure_http=self.unsecure_http,
        )
        
        job_id = response.get("id")
        self.log.info(f"AI Training job submitted successfully. Job ID: {job_id}")
        
        if self.wait_for_completion and job_id:
            self.log.info(f"Waiting for job {job_id} to complete...")
            response = hook.wait_for_job(
                job_id=job_id,
                check_interval=self.check_interval,
                timeout=self.wait_timeout,
            )
            self.log.info(f"Job {job_id} completed with status: {response.get('status', {}).get('state')}")
        
        return response


class OVHCloudAITrainingGetJobOperator(BaseOperator):
    """
    Operator to get details of an AI Training job.
    
    :param job_id: The job ID to retrieve
    :param ovh_conn_id: Connection ID for OVHcloud AI Training
    :param region: OVHcloud region (gra or bhs)
    
    Example:
        .. code-block:: python
        
            get_job = OVHCloudAITrainingGetJobOperator(
                task_id='get_job_status',
                job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
            )
    """
    
    template_fields = ("job_id",)
    
    def __init__(
        self,
        job_id: str,
        ovh_conn_id: str = OVHCloudAITrainingHook.default_conn_name,
        region: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.job_id = job_id
        self.ovh_conn_id = ovh_conn_id
        self.region = region
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the job retrieval."""
        hook = OVHCloudAITrainingHook(
            ovh_conn_id=self.ovh_conn_id,
            region=self.region,
        )
        
        response = hook.get_job(self.job_id)
        self.log.info(f"Job {self.job_id} status: {response.get('status', {}).get('state')}")
        return response


class OVHCloudAITrainingStopJobOperator(BaseOperator):
    """
    Operator to stop a running AI Training job.
    
    :param job_id: The job ID to stop
    :param ovh_conn_id: Connection ID for OVHcloud AI Training
    :param region: OVHcloud region (gra or bhs)
    
    Example:
        .. code-block:: python
        
            stop_job = OVHCloudAITrainingStopJobOperator(
                task_id='stop_job',
                job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
            )
    """
    
    template_fields = ("job_id",)
    
    def __init__(
        self,
        job_id: str,
        ovh_conn_id: str = OVHCloudAITrainingHook.default_conn_name,
        region: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.job_id = job_id
        self.ovh_conn_id = ovh_conn_id
        self.region = region
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the job stop."""
        hook = OVHCloudAITrainingHook(
            ovh_conn_id=self.ovh_conn_id,
            region=self.region,
        )
        
        response = hook.stop_job(self.job_id)
        self.log.info(f"Job {self.job_id} stop requested")
        return response


class OVHCloudAITrainingDeleteJobOperator(BaseOperator):
    """
    Operator to delete an AI Training job.
    
    :param job_id: The job ID to delete
    :param ovh_conn_id: Connection ID for OVHcloud AI Training
    :param region: OVHcloud region (gra or bhs)
    
    Example:
        .. code-block:: python
        
            delete_job = OVHCloudAITrainingDeleteJobOperator(
                task_id='delete_job',
                job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
            )
    """
    
    template_fields = ("job_id",)
    
    def __init__(
        self,
        job_id: str,
        ovh_conn_id: str = OVHCloudAITrainingHook.default_conn_name,
        region: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.job_id = job_id
        self.ovh_conn_id = ovh_conn_id
        self.region = region
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the job deletion."""
        hook = OVHCloudAITrainingHook(
            ovh_conn_id=self.ovh_conn_id,
            region=self.region,
        )
        
        response = hook.delete_job(self.job_id)
        self.log.info(f"Job {self.job_id} deleted")
        return response


class OVHCloudAITrainingGetLogsOperator(BaseOperator):
    """
    Operator to get logs of an AI Training job.
    
    :param job_id: The job ID to get logs for
    :param ovh_conn_id: Connection ID for OVHcloud AI Training
    :param region: OVHcloud region (gra or bhs)
    :param tail: Number of lines to return from the end
    
    Example:
        .. code-block:: python
        
            get_logs = OVHCloudAITrainingGetLogsOperator(
                task_id='get_job_logs',
                job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
                tail=100,
            )
    """
    
    template_fields = ("job_id",)
    
    def __init__(
        self,
        job_id: str,
        ovh_conn_id: str = OVHCloudAITrainingHook.default_conn_name,
        region: Optional[str] = None,
        tail: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.job_id = job_id
        self.ovh_conn_id = ovh_conn_id
        self.region = region
        self.tail = tail
    
    def execute(self, context: Dict[str, Any]) -> str:
        """Execute the log retrieval."""
        hook = OVHCloudAITrainingHook(
            ovh_conn_id=self.ovh_conn_id,
            region=self.region,
        )
        
        logs = hook.get_job_logs(self.job_id, tail=self.tail)
        self.log.info(f"Retrieved logs for job {self.job_id}")
        return logs


class OVHCloudAITrainingWaitForJobOperator(BaseOperator):
    """
    Operator to wait for an AI Training job to complete.
    
    :param job_id: The job ID to wait for
    :param ovh_conn_id: Connection ID for OVHcloud AI Training
    :param region: OVHcloud region (gra or bhs)
    :param target_states: States to consider as success (default: ["DONE"])
    :param failure_states: States to consider as failure
    :param check_interval: Seconds between status checks
    :param timeout: Maximum seconds to wait
    
    Example:
        .. code-block:: python
        
            wait_for_job = OVHCloudAITrainingWaitForJobOperator(
                task_id='wait_for_completion',
                job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
                timeout=7200,
            )
    """
    
    template_fields = ("job_id",)
    
    def __init__(
        self,
        job_id: str,
        ovh_conn_id: str = OVHCloudAITrainingHook.default_conn_name,
        region: Optional[str] = None,
        target_states: Optional[List[str]] = None,
        failure_states: Optional[List[str]] = None,
        check_interval: int = 30,
        timeout: int = 3600,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.job_id = job_id
        self.ovh_conn_id = ovh_conn_id
        self.region = region
        self.target_states = target_states
        self.failure_states = failure_states
        self.check_interval = check_interval
        self.timeout = timeout
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the wait operation."""
        hook = OVHCloudAITrainingHook(
            ovh_conn_id=self.ovh_conn_id,
            region=self.region,
        )
        
        self.log.info(f"Waiting for job {self.job_id} to complete...")
        response = hook.wait_for_job(
            job_id=self.job_id,
            target_states=self.target_states,
            failure_states=self.failure_states,
            check_interval=self.check_interval,
            timeout=self.timeout,
        )
        
        state = response.get("status", {}).get("state")
        self.log.info(f"Job {self.job_id} reached state: {state}")
        return response

