# AI Endpoints

OVHcloud AI Endpoints provides an OpenAI-compatible API for running LLM inference. This provider integrates seamlessly with Airflow, allowing you to use chat completions and embeddings in your workflows.

---

## Overview

AI Endpoints follows the [OpenAI API specification](https://platform.openai.com/docs/api-reference), making it easy to migrate existing workflows or use familiar patterns.

**Base URL:** `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`

---

## Connection Setup

Create an Airflow connection with your API token:

```bash
airflow connections add ovh_ai_endpoints_default \
    --conn-type generic \
    --conn-password your-api-token-here
```

See [Getting Started](getting-started.md) for detailed configuration options.

---

## Chat Completions

Generate text responses using large language models.

### Basic Usage

```python
from airflow import DAG
from apache_airflow_provider_ovhcloud_ai.operators.ai_endpoints import (
    OVHCloudAIEndpointsChatCompletionsOperator
)
from datetime import datetime

with DAG(
    dag_id='chat_completion_example',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    
    chat = OVHCloudAIEndpointsChatCompletionsOperator(
        task_id='generate_response',
        model='Meta-Llama-3_3-70B-Instruct',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain machine learning in simple terms."}
        ],
        temperature=0.7,
        max_tokens=500,
    )
```

### Message Roles

Messages use a role-based format:

| Role | Description |
|------|-------------|
| `system` | Sets the behavior and context for the assistant |
| `user` | Messages from the user |
| `assistant` | Previous responses from the model (for conversation history) |

### Multi-Turn Conversations

```python
chat = OVHCloudAIEndpointsChatCompletionsOperator(
    task_id='multi_turn_chat',
    model='Meta-Llama-3_3-70B-Instruct',
    messages=[
        {"role": "system", "content": "You are a Python expert."},
        {"role": "user", "content": "How do I read a CSV file?"},
        {"role": "assistant", "content": "You can use pandas: `pd.read_csv('file.csv')`"},
        {"role": "user", "content": "How do I filter rows where column 'age' > 30?"}
    ],
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | Required | Model name to use |
| `messages` | `List[Dict]` | Required | List of message objects |
| `temperature` | `float` | `1.0` | Controls randomness (0-2) |
| `max_tokens` | `int` | `None` | Maximum tokens to generate |
| `top_p` | `float` | `None` | Nucleus sampling parameter |
| `stop` | `str` or `List[str]` | `None` | Stop sequences |
| `ovh_conn_id` | `str` | `'ovh_ai_endpoints_default'` | Airflow connection ID |

### Response Structure

The operator returns a response matching the OpenAI format:

```python
{
    "id": "chatcmpl-xxx",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "Meta-Llama-3_3-70B-Instruct",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Machine learning is..."
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 25,
        "completion_tokens": 150,
        "total_tokens": 175
    }
}
```

---

## Embeddings

Create vector representations of text for semantic search, clustering, or classification.

### Basic Usage

```python
from apache_airflow_provider_ovhcloud_ai.operators.ai_endpoints import (
    OVHCloudAIEndpointsEmbeddingOperator
)

embed = OVHCloudAIEndpointsEmbeddingOperator(
    task_id='create_embedding',
    model='BGE-M3',
    input="Apache Airflow is a workflow orchestration tool",
)
```

### Batch Embeddings

Embed multiple texts in a single request:

```python
embed = OVHCloudAIEndpointsEmbeddingOperator(
    task_id='batch_embeddings',
    model='BGE-M3',
    input=[
        "First document to embed",
        "Second document to embed",
        "Third document to embed"
    ],
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | Required | Embedding model name |
| `input` | `str` or `List[str]` | Required | Text(s) to embed |
| `ovh_conn_id` | `str` | `'ovh_ai_endpoints_default'` | Airflow connection ID |

### Response Structure

```python
{
    "object": "list",
    "data": [
        {
            "object": "embedding",
            "index": 0,
            "embedding": [0.0023, -0.0045, ...]  # Vector of floats
        }
    ],
    "model": "BGE-M3",
    "usage": {
        "prompt_tokens": 10,
        "total_tokens": 10
    }
}
```

---

## Using the Hook Directly

For more control, use the `OVHCloudAIEndpointsHook` in Python operators:

```python
from airflow.operators.python import PythonOperator
from apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints import OVHCloudAIEndpointsHook

def custom_ai_logic(**context):
    hook = OVHCloudAIEndpointsHook(ovh_conn_id='ovh_ai_endpoints_default')
    
    # Chat completion
    response = hook.chat_completion(
        model='Meta-Llama-3_3-70B-Instruct',
        messages=[
            {"role": "user", "content": "Summarize this text: ..."}
        ],
        temperature=0.3,
        max_tokens=100,
    )
    
    summary = response['choices'][0]['message']['content']
    
    # Create embedding of the summary
    embedding_response = hook.create_embedding(
        model='BGE-M3',
        input=summary,
    )
    
    return {
        'summary': summary,
        'embedding': embedding_response['data'][0]['embedding']
    }

with DAG(...) as dag:
    task = PythonOperator(
        task_id='custom_ai_task',
        python_callable=custom_ai_logic,
    )
```

---

## Jinja Templating

Operators support Jinja templating for dynamic values:

```python
from airflow import DAG
from apache_airflow_provider_ovhcloud_ai.operators.ai_endpoints import (
    OVHCloudAIEndpointsChatCompletionsOperator
)
from datetime import datetime

with DAG(
    dag_id='templated_example',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
) as dag:
    
    chat = OVHCloudAIEndpointsChatCompletionsOperator(
        task_id='analyze_daily_data',
        model='{{ var.value.llm_model }}',  # From Airflow Variables
        messages=[
            {
                "role": "system",
                "content": "You are a data analyst."
            },
            {
                "role": "user",
                "content": "Generate a report summary for {{ ds }}"  # Execution date
            }
        ],
    )
```

### Templatable Fields

- `model`
- `messages`

---

## Available Models

Refer to the [OVHcloud AI Endpoints Catalog](https://endpoints.ai.cloud.ovh.net/catalog/) for the latest models.

### Popular Chat Models

| Model | Description |
|-------|-------------|
| `Meta-Llama-3_3-70B-Instruct` | Meta's Llama 3.3 70B instruction-tuned |
| `gpt-oss-120b` | Large open-source model |
| `Mixtral-8x22B-Instruct-v0.1` | Mixtral mixture of experts |

### Embedding Models

| Model | Description |
|-------|-------------|
| `BGE-M3` | Multilingual embedding model |
| `bge-multilingual-gemma2` | Multilingual Gemma-based embeddings |

---

## Best Practices

### 1. Use Appropriate Temperatures

- **0.0 - 0.3**: Deterministic outputs (code generation, factual answers)
- **0.5 - 0.7**: Balanced creativity (general tasks)
- **0.8 - 1.0+**: Creative outputs (brainstorming, creative writing)

### 2. Set Max Tokens Appropriately

Avoid unnecessary costs by setting `max_tokens` based on expected output length.

### 3. Use XCom for Chaining Tasks

```python
def use_previous_response(**context):
    ti = context['ti']
    response = ti.xcom_pull(task_ids='chat_task')
    content = response['choices'][0]['message']['content']
    # Process content...
```

### 4. Handle Rate Limits

For high-volume workflows, consider adding retries:

```python
chat = OVHCloudAIEndpointsChatCompletionsOperator(
    task_id='chat_with_retry',
    model='Meta-Llama-3_3-70B-Instruct',
    messages=[...],
    retries=3,
    retry_delay=timedelta(seconds=30),
)
```

---

## Error Handling

The operators raise `AirflowException` on failures. Common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| API key not found | Missing connection password | Check connection configuration |
| 401 Unauthorized | Invalid API token | Verify your token is correct |
| 429 Too Many Requests | Rate limit exceeded | Add retries with backoff |
| Model not found | Invalid model name | Check available models in the catalog |

