# AI Training

OVHcloud AI Training allows you to run machine learning training jobs on managed GPU infrastructure. This provider gives you full control over job lifecycle from your Airflow DAGs.

---

## Overview

AI Training provides:

- **Managed Infrastructure** — No need to manage servers or GPU drivers
- **Multiple GPU Types** — V100S, A100, and more
- **Object Storage Integration** — Mount your data from OVHcloud Object Storage
- **Full Job Lifecycle** — Submit, monitor, stop, and delete jobs

**Available Regions:**

| Region | Location | API Endpoint |
|--------|----------|--------------|
| `gra` | Gravelines, France | `https://gra.ai.cloud.ovh.net` |
| `bhs` | Beauharnois, Canada | `https://bhs.ai.cloud.ovh.net` |

---

## Connection Setup

Create an Airflow connection with your AI Training token:

```bash
airflow connections add ovh_ai_training_default \
    --conn-type generic \
    --conn-login gra \
    --conn-password your-ai-token-here
```

The `--conn-login` specifies the region (`gra` or `bhs`).

See [Getting Started](getting-started.md) for detailed configuration options.

---

## Operators Overview

| Operator | Description |
|----------|-------------|
| `OVHCloudAITrainingSubmitJobOperator` | Submit a new training job |
| `OVHCloudAITrainingGetJobOperator` | Get job details and status |
| `OVHCloudAITrainingWaitForJobOperator` | Wait for job completion |
| `OVHCloudAITrainingStopJobOperator` | Stop a running job |
| `OVHCloudAITrainingDeleteJobOperator` | Delete a job |
| `OVHCloudAITrainingGetLogsOperator` | Retrieve job logs |

---

## Submit a Training Job

### Basic Example

```python
from airflow import DAG
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingSubmitJobOperator
)
from datetime import datetime

with DAG(
    dag_id='simple_training_job',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    
    submit = OVHCloudAITrainingSubmitJobOperator(
        task_id='submit_training',
        image='pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime',
        name='my-training-job',
        command=['python', '-c', 'print("Hello from AI Training!")'],
        flavor='ai1-1-gpu',
    )
```

### With GPU and Environment Variables

```python
submit = OVHCloudAITrainingSubmitJobOperator(
    task_id='submit_gpu_training',
    image='pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime',
    name='gpu-training-job',
    command=['python', 'train.py'],
    flavor='ai1-1-gpu',
    gpu=1,
    gpu_model='V100S',
    env_vars={
        'EPOCHS': '100',
        'BATCH_SIZE': '32',
        'LEARNING_RATE': '0.001'
    },
)
```

### With Object Storage Volumes

Mount data from OVHcloud Object Storage:

```python
from apache_airflow_provider_ovhcloud_ai.hooks.ai_training import OVHCloudAITrainingHook

submit = OVHCloudAITrainingSubmitJobOperator(
    task_id='training_with_data',
    image='pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime',
    name='training-with-volumes',
    command=['python', 'train.py', '--data-dir', '/workspace/data'],
    flavor='ai1-1-gpu',
    volumes=[
        OVHCloudAITrainingHook.build_volume(
            container='my-training-data',
            alias='my-data-alias',
            mount_path='/workspace/data',
            permission='RO',  # Read-only
        ),
        OVHCloudAITrainingHook.build_volume(
            container='my-model-output',
            alias='my-output-alias',
            mount_path='/workspace/output',
            permission='RW',  # Read-write
        ),
    ],
)
```

### Wait for Completion

Submit a job and wait for it to finish:

```python
submit = OVHCloudAITrainingSubmitJobOperator(
    task_id='submit_and_wait',
    image='pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime',
    name='training-job',
    command=['python', 'train.py'],
    flavor='ai1-1-gpu',
    wait_for_completion=True,  # Block until job completes
    check_interval=60,         # Check every 60 seconds
    wait_timeout=7200,         # Timeout after 2 hours
)
```

---

## Submit Job Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image` | `str` | Required | Docker image to use |
| `name` | `str` | `None` | Job name |
| `command` | `List[str]` | `None` | Command to execute |
| `env_vars` | `Dict[str, str]` | `None` | Environment variables |
| `flavor` | `str` | `None` | Instance flavor (e.g., `ai1-1-gpu`) |
| `gpu` | `int` | `0` | Number of GPUs |
| `gpu_model` | `str` | `None` | GPU model (`V100S`, `A100`, etc.) |
| `cpu` | `int` | `None` | Number of CPUs |
| `volumes` | `List[Dict]` | `None` | Volume configurations |
| `labels` | `Dict[str, str]` | `None` | Job labels |
| `ssh_public_keys` | `List[str]` | `None` | SSH keys for remote access |
| `default_http_port` | `int` | `None` | HTTP port to expose |
| `job_timeout` | `int` | `None` | Job timeout in seconds |
| `unsecure_http` | `bool` | `False` | Allow unsecure HTTP |
| `wait_for_completion` | `bool` | `False` | Wait for job to complete |
| `check_interval` | `int` | `30` | Seconds between status checks |
| `wait_timeout` | `int` | `3600` | Max wait time in seconds |
| `ovh_conn_id` | `str` | `'ovh_ai_training_default'` | Connection ID |
| `region` | `str` | `None` | Override connection region |

---

## Volume Permissions

| Permission | Description |
|------------|-------------|
| `RO` | Read-only access |
| `RW` | Read-write access |
| `RWD` | Read-write-delete access |

---

## Complete Workflow Example

A complete DAG that submits a job, waits for completion, and retrieves logs:

```python
from airflow import DAG
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingSubmitJobOperator,
    OVHCloudAITrainingWaitForJobOperator,
    OVHCloudAITrainingGetLogsOperator,
    OVHCloudAITrainingDeleteJobOperator,
)
from apache_airflow_provider_ovhcloud_ai.hooks.ai_training import OVHCloudAITrainingHook
from datetime import datetime

with DAG(
    dag_id='complete_training_workflow',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['ovhcloud', 'training'],
) as dag:
    
    # Submit the training job
    submit = OVHCloudAITrainingSubmitJobOperator(
        task_id='submit_job',
        image='pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime',
        name='my-training-{{ ds_nodash }}',
        command=['python', 'train.py'],
        flavor='ai1-1-gpu',
        env_vars={
            'EPOCHS': '50',
            'MODEL_NAME': 'resnet50',
        },
        volumes=[
            OVHCloudAITrainingHook.build_volume(
                container='training-data',
                alias='data-alias',
                mount_path='/workspace/data',
                permission='RO',
            ),
            OVHCloudAITrainingHook.build_volume(
                container='model-output',
                alias='output-alias',
                mount_path='/workspace/output',
                permission='RW',
            ),
        ],
        labels={'project': 'ml-pipeline', 'env': 'production'},
    )
    
    # Wait for the job to complete
    wait = OVHCloudAITrainingWaitForJobOperator(
        task_id='wait_for_completion',
        job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
        target_states=['DONE'],
        failure_states=['FAILED', 'ERROR', 'INTERRUPTED'],
        check_interval=60,
        timeout=14400,  # 4 hours
    )
    
    # Get the logs
    logs = OVHCloudAITrainingGetLogsOperator(
        task_id='get_logs',
        job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
        tail=500,
    )
    
    # Clean up the job
    delete = OVHCloudAITrainingDeleteJobOperator(
        task_id='delete_job',
        job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
        trigger_rule='all_done',  # Run even if previous tasks failed
    )
    
    submit >> wait >> logs >> delete
```

---

## Monitor Job Status

### Get Job Details

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingGetJobOperator
)

get_status = OVHCloudAITrainingGetJobOperator(
    task_id='get_job_status',
    job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
)
```

### Wait for Specific States

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingWaitForJobOperator
)

# Wait for job to be running (useful for interactive jobs)
wait_running = OVHCloudAITrainingWaitForJobOperator(
    task_id='wait_until_running',
    job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
    target_states=['RUNNING'],
    check_interval=30,
    timeout=600,
)
```

---

## Job States

| State | Description |
|-------|-------------|
| `QUEUED` | Job is queued for execution |
| `INITIALIZING` | Job is being initialized |
| `PENDING` | Job is pending resource allocation |
| `RUNNING` | Job is currently running |
| `DONE` | Job completed successfully |
| `FAILED` | Job failed |
| `ERROR` | Job encountered an error |
| `INTERRUPTED` | Job was interrupted |
| `STOPPING` | Job is being stopped |
| `STOPPED` | Job was stopped |

---

## Stop and Delete Jobs

### Stop a Running Job

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingStopJobOperator
)

stop = OVHCloudAITrainingStopJobOperator(
    task_id='stop_job',
    job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
)
```

### Delete a Job

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_training import (
    OVHCloudAITrainingDeleteJobOperator
)

delete = OVHCloudAITrainingDeleteJobOperator(
    task_id='delete_job',
    job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
)
```

---

## Using the Hook Directly

For advanced use cases, use the hook directly:

```python
from airflow.operators.python import PythonOperator
from apache_airflow_provider_ovhcloud_ai.hooks.ai_training import OVHCloudAITrainingHook

def custom_training_logic(**context):
    hook = OVHCloudAITrainingHook(
        ovh_conn_id='ovh_ai_training_default',
        region='gra',
    )
    
    # Submit a job
    job = hook.submit_job(
        image='pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime',
        name='custom-job',
        command=['python', 'train.py'],
        flavor='ai1-1-gpu',
        env_vars=OVHCloudAITrainingHook.build_env_vars({
            'EPOCHS': '100',
        }),
    )
    
    job_id = job['id']
    print(f"Job submitted: {job_id}")
    
    # Wait for completion
    final_job = hook.wait_for_job(
        job_id=job_id,
        target_states=['DONE'],
        check_interval=60,
        timeout=7200,
    )
    
    # Get logs
    logs = hook.get_job_logs(job_id, tail=100)
    print(logs)
    
    return final_job

with DAG(...) as dag:
    task = PythonOperator(
        task_id='custom_training',
        python_callable=custom_training_logic,
    )
```

---

## Helper Methods

### Build Volume Configuration

```python
from apache_airflow_provider_ovhcloud_ai.hooks.ai_training import OVHCloudAITrainingHook

volume = OVHCloudAITrainingHook.build_volume(
    container='my-bucket',           # Object Storage container name
    alias='my-data-alias',           # Data store alias
    mount_path='/workspace/data',    # Mount path in container
    prefix='datasets/v1',            # Optional: subfolder in container
    permission='RO',                 # RO, RW, or RWD
    cache=True,                      # Enable caching
)
```

### Build Environment Variables

```python
from apache_airflow_provider_ovhcloud_ai.hooks.ai_training import OVHCloudAITrainingHook

env_vars = OVHCloudAITrainingHook.build_env_vars({
    'EPOCHS': '100',
    'BATCH_SIZE': '32',
    'LEARNING_RATE': '0.001',
})
# Returns: [{"name": "EPOCHS", "value": "100"}, ...]
```

---

## Best Practices

### 1. Use Labels for Organization

```python
submit = OVHCloudAITrainingSubmitJobOperator(
    task_id='submit_job',
    image='...',
    labels={
        'project': 'recommendation-engine',
        'team': 'ml-platform',
        'env': 'production',
        'dag_id': '{{ dag.dag_id }}',
        'run_id': '{{ run_id }}',
    },
)
```

### 2. Set Appropriate Timeouts

```python
submit = OVHCloudAITrainingSubmitJobOperator(
    task_id='submit_job',
    image='...',
    job_timeout=14400,       # Job timeout: 4 hours
    wait_for_completion=True,
    wait_timeout=16000,      # Airflow wait timeout: slightly longer
)
```

### 3. Use Trigger Rules for Cleanup

```python
delete = OVHCloudAITrainingDeleteJobOperator(
    task_id='cleanup_job',
    job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
    trigger_rule='all_done',  # Always run, even on failure
)
```

### 4. Separate Submit and Wait for Long Jobs

For very long jobs, separate the submit and wait operators:

```python
submit = OVHCloudAITrainingSubmitJobOperator(
    task_id='submit_job',
    wait_for_completion=False,  # Don't block
    ...
)

# Use a sensor or separate DAG run for monitoring
wait = OVHCloudAITrainingWaitForJobOperator(
    task_id='wait_for_job',
    job_id='{{ ti.xcom_pull(task_ids="submit_job")["id"] }}',
    timeout=86400,  # 24 hours
    poke_interval=300,  # Check every 5 minutes
)
```

---

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid region | Wrong region specified | Use `gra` or `bhs` |
| Token not found | Missing connection password | Check connection config |
| Job failed | Training script error | Check job logs |
| Timeout waiting | Job took too long | Increase `wait_timeout` |
| Invalid flavor | Unknown instance type | Check available flavors |

