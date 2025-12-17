# Apache Airflow Provider for OVHcloud AI

![Hero image](assets/header.png)

Welcome to the documentation for the **Apache Airflow Provider for OVHcloud AI** — a seamless integration between [Apache Airflow](https://airflow.apache.org/) and [OVHcloud AI products](https://www.ovhcloud.com/en/public-cloud/ai-machine-learning/).

---

## Overview

This provider enables you to orchestrate AI workloads on OVHcloud infrastructure directly from your Airflow DAGs. It supports two main OVHcloud AI products:

<div class="grid cards" markdown>

-   :material-chat-processing:{ .lg .middle } **AI Endpoints**

    ---

    OpenAI-compatible API for running LLM inference with chat completions and embeddings.

    [:octicons-arrow-right-24: AI Endpoints docs](ai-endpoints.md)

-   :material-brain:{ .lg .middle } **AI Training**

    ---

    Managed training jobs on GPU clusters with full lifecycle management.

    [:octicons-arrow-right-24: AI Training docs](ai-training.md)

</div>

---

## Features

### AI Endpoints
- ✅ **Chat Completions** — Generate text using various LLM models
- ✅ **Embeddings** — Create vector embeddings for text
- ✅ **OpenAI Compatible** — Follows the OpenAI API specification
- ✅ **Templating Support** — Dynamic messages and model selection with Jinja templates

### AI Training
- ✅ **Job Submission** — Submit training jobs with custom Docker images
- ✅ **GPU Support** — Access to V100S, A100, and other GPU models
- ✅ **Volume Mounting** — Mount OVHcloud Object Storage containers
- ✅ **Job Monitoring** — Track job status, wait for completion, retrieve logs
- ✅ **Full Lifecycle** — Submit, monitor, stop, and delete jobs

---

## Quick Start

### Installation

=== "pip"

    ``` bash
    pip install apache-airflow-provider-ovhcloud-ai
    ```

=== "uv"

    ``` bash
    uv init \
    uv add apache-airflow-provider-ovhcloud-ai
    ```

### Minimal Example

```python
from airflow import DAG
from apache_airflow_provider_ovhcloud_ai.operators.ai_endpoints import OVHCloudAIEndpointsChatCompletionsOperator, OVHCloudAIEndpointsEmbeddingOperator

from apache_airflow_provider_ovhcloud_ai.operators.ai_training import OVHCloudAITrainingSubmitJobOperator
from apache_airflow_provider_ovhcloud_ai.hooks.ai_training import OVHCloudAITrainingHook

from datetime import datetime

with DAG(
    dag_id='ovh_ai_example',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    
    chat_task = OVHCloudAIEndpointsChatCompletionsOperator(
        task_id='generate_response',
        model='gpt-oss-120b',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain what Apache Airflow is in one sentence."}
        ],
        temperature=0.7,
        max_tokens=100,
    )

    embedding_task = OVHCloudAIEndpointsEmbeddingOperator(
        task_id='create_embedding',
        model='BGE-M3',
        input="Text to embed"
    )

    submit_job = OVHCloudAITrainingSubmitJobOperator(
        task_id='submit_training',
        image='pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime',
        name='my-training-job',
        command=['python', 'hello_world.py'],
        flavor='ai1-1-gpu',
        env_vars={"EPOCHS": "100", "BATCH_SIZE": "32"},
        volumes=[
            OVHCloudAITrainingHook.build_volume(
                container="input",
                mount_path="/workspace",
                permission="RO",
                alias="input"
            ),
            OVHCloudAITrainingHook.build_volume(
                container="output",
                mount_path="/workspace/output",
                permission="RWD",
                alias="output"
            ),
        ],
        wait_for_completion=True,
        wait_timeout=7200,
    )
```

---

## Supported Airflow Versions

| Airflow Version | Support Status |
|-----------------|----------------|
| 2.3.x           | ✅ Supported    |
| 2.4.x           | ✅ Supported    |
| 2.5.x           | ✅ Supported    |
| 2.6.x           | ✅ Supported    |
| 2.7.x+          | ✅ Supported    |

---

## Requirements

- Python >= 3.8
- Apache Airflow >= 2.3.0
- An OVHcloud account with a Public Cloud project

---

## Getting Help

- 📖 [GitHub Repository](https://github.com/ovh/apache-airflow-provider-ovhcloud-ai)
- 🐛 [Issue Tracker](https://github.com/ovh/apache-airflow-provider-ovhcloud-ai/issues)
- 💬 [Discussions](https://github.com/ovh/apache-airflow-provider-ovhcloud-ai/discussions)
- 🌐 [OVHcloud AI Documentation](https://help.ovhcloud.com/csm/en-ie-documentation-public-cloud-ai-and-machine-learning?id=kb_browse_cat&kb_id=574a8325551974502d4c6e78b7421938&kb_category=1f34d555f49801102d4ca4d466a7fd7d&spa=1)

---

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/ovh/apache-airflow-provider-ovhcloud-ai/blob/master/LICENSE) file for details.

