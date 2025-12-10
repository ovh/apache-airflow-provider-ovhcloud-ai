# Getting Started

This guide will help you install and configure the Apache Airflow Provider for OVHcloud AI.

---

## Installation

Install the provider package using pip or uv:

=== "pip"

    ``` bash
    pip install apache-airflow-provider-ovhcloud-ai
    ```

=== "uv"

    ``` bash
    uv init \
    uv add apache-airflow-provider-ovhcloud-ai
    ```


---

## Configuration

Before using the operators, you need to configure Airflow connections for the OVHcloud services you want to use.

### AI Endpoints Connection

#### Option 1: Using the Airflow UI

1. Navigate to **Admin > Connections** in the Airflow UI
2. Click **+ Add a new record**
3. Fill in the connection details:

| Field | Value |
|-------|-------|
| **Connection Id** | `ovh_ai_endpoints_default` |
| **Connection Type** | `generic` |
| **Password** | Your OVHcloud AI Endpoints API token |

#### Option 2: Using the Airflow CLI

```bash
airflow connections add ovh_ai_endpoints_default \
    --conn-type generic \
    --conn-password your-api-token-here
```

#### Option 3: Using Environment Variables

```bash
export AIRFLOW_CONN_OVH_AI_ENDPOINTS_DEFAULT='{"password":"your-api-token-here"}'
```

---

### AI Training Connection

#### Option 1: Using the Airflow UI

1. Navigate to **Admin > Connections** in the Airflow UI
2. Click **+ Add a new record**
3. Fill in the connection details:

| Field | Value |
|-------|-------|
| **Connection Id** | `ovh_ai_training_default` |
| **Connection Type** | `generic` |
| **Login** | Region (`gra` or `bhs`) |
| **Password** | Your OVHcloud AI Training token |

#### Option 2: Using the Airflow CLI

```bash
airflow connections add ovh_ai_training_default \
    --conn-type ai_training \
    --conn-login gra \
    --conn-password your-ai-token-here
```

#### Option 3: Using Environment Variables

```bash
export AIRFLOW_CONN_OVH_AI_TRAINING_DEFAULT='{"login":"gra","password":"your-ai-token-here"}'
```

---

## Getting Your API Tokens

### AI Endpoints Token

1. Go to the [OVHcloud Manager](https://www.ovh.com/manager/)
2. Navigate to **Public Cloud > AI Endpoints**
3. Generate or copy your API token

### AI Training Token

1. Go to the [OVHcloud Manager](https://www.ovh.com/manager/)
2. Navigate to **Public Cloud > AI Dashboard > Tokens**
3. Generate or copy your AI Training token

---

## Available Regions

### AI Training Regions

| Region | Location | API Endpoint |
|--------|----------|--------------|
| `gra` | Gravelines, France | `https://gra.ai.cloud.ovh.net` |
| `bhs` | Beauharnois, Canada | `https://bhs.ai.cloud.ovh.net` |

---

## Testing Your Connection

You can verify your connections are working correctly using the Airflow UI:

1. Go to **Admin > Connections**
2. Find your connection (e.g., `ovh_ai_endpoints_default`)
3. Click **Test** to verify the connection

Or test programmatically:

```python
from apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints import OVHCloudAIEndpointsHook

hook = OVHCloudAIEndpointsHook()
success, message = hook.test_connection()
print(f"Connection test: {message}")
```

---

## Your First DAG

Here's a complete example DAG that uses OVHcloud AI Endpoints:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from apache_airflow_provider_ovhcloud_ai.operators.ai_endpoints import (
    OVHCloudAIEndpointsChatCompletionsOperator
)
from datetime import datetime

def process_response(**context):
    """Process the LLM response from the previous task."""
    ti = context['ti']
    response = ti.xcom_pull(task_ids='generate_text')
    
    content = response['choices'][0]['message']['content']
    tokens_used = response['usage']['total_tokens']
    
    print(f"Response: {content}")
    print(f"Tokens used: {tokens_used}")
    
    return content

with DAG(
    dag_id='my_first_ovhcloud_ai_dag',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['ovhcloud', 'ai'],
) as dag:
    
    generate = OVHCloudAIEndpointsChatCompletionsOperator(
        task_id='generate_text',
        model='Meta-Llama-3_3-70B-Instruct',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Apache Airflow?"}
        ],
        temperature=0.7,
        max_tokens=200,
    )
    
    process = PythonOperator(
        task_id='process_response',
        python_callable=process_response,
    )
    
    generate >> process
```

---

## Next Steps

Now that you have the provider installed and configured, explore the specific features:

- [AI Endpoints](ai-endpoints.md) — Learn about chat completions and embeddings
- [AI Training](ai-training.md) — Learn about submitting and managing training jobs
- [API Reference](api-reference.md) — Complete API documentation

