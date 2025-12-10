# SPDX-License-Identifier: Apache-2.0
from typing import Any, Dict, List, Optional
import requests
from airflow.sdk.bases.hook import BaseHook
from airflow.exceptions import AirflowException


class OVHCloudAITrainingHook(BaseHook):
    """
    Hook to interact with OVHcloud AI Training API.
    
    This hook provides methods to create, manage and monitor AI Training jobs
    on OVHcloud infrastructure.
    
    :param ovh_conn_id: Connection ID for OVHcloud AI Training
    :param region: OVHcloud region (gra or bhs)
    :param timeout: Request timeout in seconds
    
    Example connection configuration:
        - Conn Id: ovh_ai_training_default
        - Conn Type: ai_training
        - Password: your-ai-token
        - Extra: {"region": "gra"}
    """
    
    conn_name_attr = "ovh_conn_id"
    default_conn_name = "ovh_ai_training_default"
    conn_type = "ai_training"
    hook_name = "OVHcloud AI Training"
    
    REGIONS = {
        "gra": "https://gra.ai.cloud.ovh.net",
        "bhs": "https://bhs.ai.cloud.ovh.net",
    }
    
    def __init__(
        self,
        ovh_conn_id: str = default_conn_name,
        region: Optional[str] = None,
        timeout: int = 120,
    ) -> None:
        super().__init__()
        self.ovh_conn_id = ovh_conn_id
        self._region = region
        self.timeout = timeout
        self._token = None
        self._base_url = None
        
    def get_conn(self) -> str:
        """Get the API token from Airflow connection."""
        if self._token is None:
            conn = self.get_connection(self.ovh_conn_id)
            self._token = conn.password
            
            if not self._token:
                raise AirflowException(
                    f"OVHcloud AI Training token not found in connection '{self.ovh_conn_id}'. "
                    "Please set it in the password field."
                )
            
            # Get region from login
            if self._region is None:
                self._region = conn.login
            
            if self._region not in self.REGIONS:
                raise AirflowException(
                    f"Invalid region '{self._region}'. Valid regions are: {list(self.REGIONS.keys())}"
                )
            
            self._base_url = self.REGIONS[self._region]
            
        return self._token
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization."""
        token = self.get_conn()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to OVHcloud AI Training API."""
        self.get_conn()  # Ensure connection is initialized
        url = f"{self._base_url}/{endpoint}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except requests.exceptions.RequestException as e:
            raise AirflowException(f"Request to OVHcloud AI Training failed: {str(e.response.text)}")
    
    def submit_job(
        self,
        image: str,
        default_http_port: Optional[int] = None,
        name: Optional[str] = None,
        command: Optional[List[str]] = None,
        env_vars: Optional[List[Dict[str, str]]] = None,
        gpu: int = 0,
        gpu_model: Optional[str] = None,
        cpu: Optional[int] = None,
        flavor: Optional[str] = None,
        volumes: Optional[List[Dict[str, Any]]] = None,
        labels: Optional[Dict[str, str]] = None,
        ssh_public_keys: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        timeout_auto_restart: Optional[bool] = None,
        unsecure_http: bool = False,
        read_user: Optional[str] = None,
        shutdown: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Submit a new AI Training job.
        
        See API spec: https://bhs.ai.cloud.ovh.net/#/operations/jobNew
        
        :param image: Docker image to use for the job
        :param default_http_port: Default HTTP port exposed by the job
        :param name: Optional name for the job
        :param command: Command to execute in the container (overrides image CMD)
        :param env_vars: Environment variables as list of {"name": "X", "value": "Y"}
        :param gpu: Number of GPUs to allocate (default: 0)
        :param gpu_model: GPU model to use (e.g., "V100S", "A100")
        :param cpu: Number of CPUs to allocate
        :param flavor: Specific flavor/instance type to use (e.g., "ai1-1-gpu")
        :param volumes: List of volume configurations to mount
        :param labels: Labels to attach to the job (dict of key-value pairs)
        :param ssh_public_keys: SSH public keys for remote access
        :param timeout: Job timeout in seconds
        :param timeout_auto_restart: Whether to auto-restart on timeout
        :param unsecure_http: Allow unsecure HTTP access (default: False)
        :param read_user: User allowed to read job output
        :param shutdown: Shutdown strategy ("Normal" or "Fast")
        :param kwargs: Additional parameters to pass to the API
        :return: API response with job details
        
        Example volumes format:
            [
                {
                    "dataStore": {
                        "alias": "my-data-alias",
                        "container": "my-container"
                    },
                    "mountPath": "/workspace/data",
                    "permission": "RO",  # "RO" or "RW" or "RWD"
                    "cache": False
                }
            ]
            
        Example env_vars format:
            [
                {"name": "EPOCHS", "value": "100"},
                {"name": "LEARNING_RATE", "value": "0.001"}
            ]
        
        Example with flavor:
            hook.submit_job(
                image="pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime",
                flavor="ai1-1-gpu",
                command=["python", "train.py"],
            )
        """
        # Build resources object
        resources: Dict[str, Any] = {}
        if flavor:
            resources["flavor"] = flavor
        if gpu is not None:
            resources["gpu"] = gpu
        if gpu_model:
            resources["gpuModel"] = gpu_model
        if cpu is not None:
            resources["cpu"] = cpu
            
        # Build job spec
        job_spec: Dict[str, Any] = {
            "image": image,
            "unsecureHttp": unsecure_http,
        }
        
        # Add resources if any are specified
        if resources:
            job_spec["resources"] = resources
            
        # Optional fields
        if name:
            job_spec["name"] = name
        if default_http_port is not None:
            job_spec["defaultHttpPort"] = default_http_port
        if command:
            job_spec["command"] = command
        if env_vars:
            job_spec["envVars"] = env_vars
        if volumes:
            job_spec["volumes"] = volumes
        if labels:
            job_spec["labels"] = labels
        if ssh_public_keys:
            job_spec["sshPublicKeys"] = ssh_public_keys
        if timeout is not None:
            job_spec["timeout"] = timeout
        if timeout_auto_restart is not None:
            job_spec["timeoutAutoRestart"] = timeout_auto_restart
        if read_user:
            job_spec["readUser"] = read_user
        if shutdown:
            job_spec["shutdown"] = shutdown
            
        # Add any extra kwargs
        job_spec.update(kwargs)
        
        self.log.info(f"Submitting AI Training job with image: {image}")
        return self._make_request("POST", "v1/job", data=job_spec)
    
    @staticmethod
    def build_volume(
        container: str,
        mount_path: str,
        alias: str,
        prefix: Optional[str] = None,
        permission: str = "RO",
        cache: bool = False,
    ) -> Dict[str, Any]:
        """
        Helper to build a volume configuration for submit_job.
        
        :param container: Object storage container name
        :param mount_path: Path where the volume will be mounted in the container
        :param alias: Data store alias (if using named data stores)
        :param prefix: Prefix path within the container
        :param permission: Access permission - "RO" (read-only), "RW" (read-write), 
                          or "RWD" (read-write-delete)
        :param cache: Enable caching for the volume
        :return: Volume configuration dict
        
        Example:
            volume = OVHCloudAITrainingHook.build_volume(
                container="my-training-data",
                mount_path="/workspace/data",
                permission="RO",
            )
        """
        data_store: Dict[str, str] = {"container": container, "alias": alias}
        if prefix:
            data_store["prefix"] = prefix
            
        return {
            "volumeSource": {
                "dataStore": data_store
            },
            "mountPath": mount_path,
            "permission": permission,
            "cache": cache,
        }
    
    @staticmethod
    def build_env_vars(env_dict: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Helper to convert a dict of environment variables to API format.
        
        :param env_dict: Dictionary of environment variable names and values
        :return: List of env var objects for the API
        
        Example:
            env_vars = OVHCloudAITrainingHook.build_env_vars({
                "EPOCHS": "100",
                "BATCH_SIZE": "32",
            })
        """
        return [{"name": k, "value": str(v)} for k, v in env_dict.items()]
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """
        Get details of a specific job.
        
        :param job_id: The job ID to retrieve
        :return: Job details
        """
        self.log.info(f"Getting AI Training job: {job_id}")
        return self._make_request("GET", f"v1/job/{job_id}")
    
    def get_job_status(self, job_id: str) -> str:
        """
        Get the status of a specific job.
        
        :param job_id: The job ID to check
        :return: Job status string
        """
        job = self.get_job(job_id)
        return job.get("status", {}).get("state", "UNKNOWN")
    
    def list_jobs(
        self,
        page: int = 1,
        size: int = 100,
        state: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        List AI Training jobs.
        
        :param page: Page number for pagination
        :param size: Number of results per page
        :param state: Filter by job state
        :param labels: Filter by labels
        :return: List of jobs
        """
        params = {"page": page, "size": size}
        if state:
            params["state"] = state
        if labels:
            params["labels"] = ",".join(f"{k}={v}" for k, v in labels.items())
            
        self.log.info("Listing AI Training jobs")
        return self._make_request("GET", "v1/job", params=params)
    
    def stop_job(self, job_id: str) -> Dict[str, Any]:
        """
        Stop a running job.
        
        :param job_id: The job ID to stop
        :return: API response
        """
        self.log.info(f"Stopping AI Training job: {job_id}")
        return self._make_request("PUT", f"v1/job/{job_id}/kill")
    
    def delete_job(self, job_id: str) -> Dict[str, Any]:
        """
        Delete a job.
        
        :param job_id: The job ID to delete
        :return: API response
        """
        self.log.info(f"Deleting AI Training job: {job_id}")
        return self._make_request("DELETE", f"v1/job/{job_id}")
    
    def get_job_logs(
        self,
        job_id: str,
        since: Optional[str] = None,
        tail: Optional[int] = None,
    ) -> str:
        """
        Get logs for a job.
        
        :param job_id: The job ID to get logs for
        :param since: Only return logs after this timestamp
        :param tail: Number of lines to return from the end
        :return: Job logs as string
        """
        params = {}
        if since:
            params["since"] = since
        if tail:
            params["tail"] = tail
            
        self.log.info(f"Getting logs for AI Training job: {job_id}")
        result = self._make_request("GET", f"v1/job/{job_id}/log", params=params)
        
        return result
    
    def wait_for_job(
        self,
        job_id: str,
        target_states: Optional[List[str]] = None,
        failure_states: Optional[List[str]] = None,
        check_interval: int = 30,
        timeout: int = 3600,
    ) -> Dict[str, Any]:
        """
        Wait for a job to reach a target state.
        
        :param job_id: The job ID to wait for
        :param target_states: States to consider as success (default: ["DONE"])
        :param failure_states: States to consider as failure (default: ["FAILED", "ERROR"])
        :param check_interval: Seconds between status checks
        :param timeout: Maximum seconds to wait
        :return: Final job details
        :raises AirflowException: If job enters failure state or timeout
        """
        import time
        
        if target_states is None:
            target_states = ["DONE"]
        if failure_states is None:
            failure_states = ["FAILED", "ERROR", "INTERRUPTED"]
            
        start_time = time.time()
        
        while True:
            job = self.get_job(job_id)
            state = job.get("status", {}).get("state", "UNKNOWN")
            
            self.log.info(f"Job {job_id} status: {state}")
            
            if state in target_states:
                return job
                
            if state in failure_states:
                raise AirflowException(
                    f"AI Training job {job_id} entered failure state: {state}"
                )
                
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise AirflowException(
                    f"Timeout waiting for AI Training job {job_id}. "
                    f"Last state: {state}"
                )
                
            time.sleep(check_interval)
    
    def test_connection(self) -> tuple[bool, str]:
        """Test the connection to OVHcloud AI Training."""
        try:
            self.get_conn()
            # Try to list jobs to verify the token works
            self.list_jobs(page=1, size=1)
            return True, "Connection successfully tested"
        except Exception as e:
            return False, str(e)

