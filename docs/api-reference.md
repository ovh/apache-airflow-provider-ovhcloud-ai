# API Reference

Complete API reference for all hooks and operators in the Apache Airflow Provider for OVHcloud AI.

---

## AI Endpoints

### OVHCloudAIEndpointsHook

Hook to interact with OVHcloud AI Endpoints API.

```python
from apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints import OVHCloudAIEndpointsHook
```

#### Constructor

```python
OVHCloudAIEndpointsHook(
    ovh_conn_id: str = 'ovh_ai_endpoints_default',
    timeout: int = 60,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ovh_conn_id` | `str` | `'ovh_ai_endpoints_default'` | Airflow connection ID |
| `timeout` | `int` | `60` | Request timeout in seconds |

#### Methods

##### `chat_completion`

Create a chat completion.

```python
hook.chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    stream: bool = False,
    stop: Optional[Union[str, List[str]]] = None,
    **kwargs,
) -> Dict[str, Any]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `str` | Model name to use |
| `messages` | `List[Dict]` | List of message objects with `role` and `content` |
| `temperature` | `float` | Sampling temperature (0-2) |
| `max_tokens` | `int` | Maximum tokens to generate |
| `top_p` | `float` | Nucleus sampling parameter |
| `stream` | `bool` | Whether to stream responses |
| `stop` | `str` or `List[str]` | Stop sequences |

##### `create_embedding`

Create embeddings for text.

```python
hook.create_embedding(
    model: str,
    input: Union[str, List[str]],
    **kwargs,
) -> Dict[str, Any]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `str` | Embedding model name |
| `input` | `str` or `List[str]` | Text(s) to embed |

##### `test_connection`

Test the connection to OVHcloud AI Endpoints.

```python
hook.test_connection() -> tuple[bool, str]
```

Returns a tuple of `(success: bool, message: str)`.

---

### OVHCloudAIEndpointsChatCompletionsOperator

Operator to perform chat completion.

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_endpoints import (
    OVHCloudAIEndpointsChatCompletionsOperator
)
```

#### Constructor

```python
OVHCloudAIEndpointsChatCompletionsOperator(
    task_id: str,
    model: str,
    messages: List[Dict[str, str]],
    ovh_conn_id: str = 'ovh_ai_endpoints_default',
    temperature: float = 1.0,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    stop: Optional[Union[str, List[str]]] = None,
    stream: bool = False,
    **kwargs,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | Required | Model name to use |
| `messages` | `List[Dict]` | Required | Chat messages |
| `ovh_conn_id` | `str` | `'ovh_ai_endpoints_default'` | Connection ID |
| `temperature` | `float` | `1.0` | Sampling temperature |
| `max_tokens` | `int` | `None` | Maximum tokens |
| `top_p` | `float` | `None` | Nucleus sampling |
| `stop` | `str`/`List[str]` | `None` | Stop sequences |
| `stream` | `bool` | `False` | Stream responses |

#### Template Fields

- `model`
- `messages`

---

### OVHCloudAIEndpointsEmbeddingOperator

Operator to create embeddings.

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_endpoints import (
    OVHCloudAIEndpointsEmbeddingOperator
)
```

#### Constructor

```python
OVHCloudAIEndpointsEmbeddingOperator(
    task_id: str,
    model: str,
    input: Union[str, List[str]],
    ovh_conn_id: str = 'ovh_ai_endpoints_default',
    **kwargs,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | Required | Embedding model name |
| `input` | `str`/`List[str]` | Required | Text(s) to embed |
| `ovh_conn_id` | `str` | `'ovh_ai_endpoints_default'` | Connection ID |

#### Template Fields

- `model`
- `input`

---

## AI Training

### OVHCloudAITrainingHook

Hook to interact with OVHcloud AI Training API.

```python
from apache_airflow_provider_ovhcloud_ai.hooks.ai_training import OVHCloudAITrainingHook
```

#### Constructor

```python
OVHCloudAITrainingHook(
    ovh_conn_id: str = 'ovh_ai_training_default',
    region: Optional[str] = None,
    timeout: int = 120,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ovh_conn_id` | `str` | `'ovh_ai_training_default'` | Connection ID |
| `region` | `str` | `None` | Region (`gra` or `bhs`) |
| `timeout` | `int` | `120` | Request timeout |

#### Methods

##### `submit_job`

Submit a new AI Training job.

```python
hook.submit_job(
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
    **kwargs,
) -> Dict[str, Any]
```

##### `get_job`

Get details of a specific job.

```python
hook.get_job(job_id: str) -> Dict[str, Any]
```

##### `get_job_status`

Get the status of a specific job.

```python
hook.get_job_status(job_id: str) -> str
```

##### `list_jobs`

List AI Training jobs.

```python
hook.list_jobs(
    page: int = 1,
    size: int = 100,
    state: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]
```

##### `stop_job`

Stop a running job.

```python
hook.stop_job(job_id: str) -> Dict[str, Any]
```

##### `delete_job`

Delete a job.

```python
hook.delete_job(job_id: str) -> Dict[str, Any]
```

##### `get_job_logs`

Get logs for a job.

```python
hook.get_job_logs(
    job_id: str,
    since: Optional[str] = None,
    tail: Optional[int] = None,
) -> str
```

##### `wait_for_job`

Wait for a job to reach a target state.

```python
hook.wait_for_job(
    job_id: str,
    target_states: Optional[List[str]] = None,
    failure_states: Optional[List[str]] = None,
    check_interval: int = 30,
    timeout: int = 3600,
) -> Dict[str, Any]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `job_id` | `str` | Required | Job ID to wait for |
| `target_states` | `List[str]` | `['DONE']` | Success states |
| `failure_states` | `List[str]` | `['FAILED', 'ERROR', 'INTERRUPTED']` | Failure states |
| `check_interval` | `int` | `30` | Seconds between checks |
| `timeout` | `int` | `3600` | Max wait time |

##### `test_connection`

Test the connection to OVHcloud AI Training.

```python
hook.test_connection() -> tuple[bool, str]
```

#### Static Methods

##### `build_volume`

Helper to build a volume configuration.

```python
OVHCloudAITrainingHook.build_volume(
    container: str,
    mount_path: str,
    alias: str,
    prefix: Optional[str] = None,
    permission: str = 'RO',
    cache: bool = False,
) -> Dict[str, Any]
```

##### `build_env_vars`

Helper to convert a dict of environment variables to API format.

```python
OVHCloudAITrainingHook.build_env_vars(
    env_dict: Dict[str, str]
) -> List[Dict[str, str]]
```

---

### OVHCloudAITrainingSubmitJobOperator

Operator to submit an AI Training job.

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingSubmitJobOperator
)
```

#### Constructor

```python
OVHCloudAITrainingSubmitJobOperator(
    task_id: str,
    image: str,
    ovh_conn_id: str = 'ovh_ai_training_default',
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
    **kwargs,
)
```

#### Template Fields

- `image`
- `name`
- `command`
- `env_vars`
- `labels`

---

### OVHCloudAITrainingGetJobOperator

Operator to get details of an AI Training job.

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingGetJobOperator
)
```

#### Constructor

```python
OVHCloudAITrainingGetJobOperator(
    task_id: str,
    job_id: str,
    ovh_conn_id: str = 'ovh_ai_training_default',
    region: Optional[str] = None,
    **kwargs,
)
```

#### Template Fields

- `job_id`

---

### OVHCloudAITrainingWaitForJobOperator

Operator to wait for an AI Training job to complete.

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingWaitForJobOperator
)
```

#### Constructor

```python
OVHCloudAITrainingWaitForJobOperator(
    task_id: str,
    job_id: str,
    ovh_conn_id: str = 'ovh_ai_training_default',
    region: Optional[str] = None,
    target_states: Optional[List[str]] = None,
    failure_states: Optional[List[str]] = None,
    check_interval: int = 30,
    timeout: int = 3600,
    **kwargs,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `job_id` | `str` | Required | Job ID to wait for |
| `target_states` | `List[str]` | `['DONE']` | Success states |
| `failure_states` | `List[str]` | `['FAILED', 'ERROR', 'INTERRUPTED']` | Failure states |
| `check_interval` | `int` | `30` | Check interval |
| `timeout` | `int` | `3600` | Max wait time |

#### Template Fields

- `job_id`

---

### OVHCloudAITrainingStopJobOperator

Operator to stop a running AI Training job.

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingStopJobOperator
)
```

#### Constructor

```python
OVHCloudAITrainingStopJobOperator(
    task_id: str,
    job_id: str,
    ovh_conn_id: str = 'ovh_ai_training_default',
    region: Optional[str] = None,
    **kwargs,
)
```

#### Template Fields

- `job_id`

---

### OVHCloudAITrainingDeleteJobOperator

Operator to delete an AI Training job.

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingDeleteJobOperator
)
```

#### Constructor

```python
OVHCloudAITrainingDeleteJobOperator(
    task_id: str,
    job_id: str,
    ovh_conn_id: str = 'ovh_ai_training_default',
    region: Optional[str] = None,
    **kwargs,
)
```

#### Template Fields

- `job_id`

---

### OVHCloudAITrainingGetLogsOperator

Operator to get logs of an AI Training job.

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingGetLogsOperator
)
```

#### Constructor

```python
OVHCloudAITrainingGetLogsOperator(
    task_id: str,
    job_id: str,
    ovh_conn_id: str = 'ovh_ai_training_default',
    region: Optional[str] = None,
    tail: Optional[int] = None,
    **kwargs,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `job_id` | `str` | Required | Job ID |
| `tail` | `int` | `None` | Lines from end |

#### Template Fields

- `job_id`

---

## Connection Configuration

### AI Endpoints Connection

| Field | Value |
|-------|-------|
| Connection Id | `ovh_ai_endpoints_default` |
| Connection Type | `generic` |
| Password | Your API token |

### AI Training Connection

| Field | Value |
|-------|-------|
| Connection Id | `ovh_ai_training_default` |
| Connection Type | `generic` |
| Login | Region (`gra` or `bhs`) |
| Password | Your AI Training token |

---

## Constants

### AI Training Regions

```python
OVHCloudAITrainingHook.REGIONS = {
    "gra": "https://gra.ai.cloud.ovh.net",
    "bhs": "https://bhs.ai.cloud.ovh.net",
}
```

### AI Endpoints Base URL

```python
OVHCloudAIEndpointsHook.BASE_URL = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"
```

---

## Exceptions

All operators and hooks raise `AirflowException` on failures:

```python
from airflow.exceptions import AirflowException

try:
    hook = OVHCloudAITrainingHook()
    job = hook.submit_job(image='...')
except AirflowException as e:
    print(f"Error: {e}")
```

Common exception messages:

- `"OVHcloud AI Training token not found in connection '...'"` — Missing password in connection
- `"Invalid region '...'. Valid regions are: ['gra', 'bhs']"` — Invalid region specified
- `"AI Training job ... entered failure state: ..."` — Job failed
- `"Timeout waiting for AI Training job ..."` — Wait timeout exceeded
- `"Request to OVHcloud AI ... failed: ..."` — API request error

