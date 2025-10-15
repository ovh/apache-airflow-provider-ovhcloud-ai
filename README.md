# Apache Airflow Provider for OVHcloud AI

This package provides Apache Airflow integration with [OVHcloud AI products](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/): 
- **AI Endpoints**: an OpenAI-compatible API service for running LLM inference

## AI Endpoints

### Features

- ✅ **Chat Completions**: Generate text using various LLM models
- ✅ **Embeddings**: Create vector embeddings for text
- ✅ **OpenAI Compatible**: Follows the OpenAI API specification
- ✅ **Airflow Native**: Built specifically for Apache Airflow workflows
- ✅ **Templating Support**: Dynamic messages and model selection with Jinja templates

### Installation

```bash
pip install apache-airflow-provider-ovhcloud-ai
```

### Configuration

#### 1. Create an Airflow Connection

Navigate to **Admin > Connections** in the Airflow UI and create a new connection:

- **Connection Id**: `ovh_ai_endpoints_default` (or your custom name)
- **Connection Type**: `generic`
- **Password**: Your OVHcloud AI Endpoints API token

Alternatively, use the Airflow CLI:

```bash
airflow connections add ovh_ai_endpoints_default \
    --conn-type generic \
    --conn-password your-api-token-here
```

Or set via environment variable:

```bash
export AIRFLOW_CONN_OVH_AI_ENDPOINTS_DEFAULT='{"password":"your-api-token-here"}'
```

#### 2. Get Your API Token

Obtain your API token from the [OVHcloud manager](https://www.ovh.com/manager/).

### Usage

#### Chat Completion Example

```python
from airflow import DAG
from apache_airflow_provider_ovhcloud_ai.operators.ai_endpoints import OVHCloudAIEndpointsChatCompletionsOperator
from datetime import datetime

with DAG(
    dag_id='ovh_ai_chat_example',
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
```

#### Embedding Example

```python
from airflow import DAG
from apache_airflow_provider_ovhcloud_ai.operators.ovhcloud_ai import OVHCloudAIEndpointsEmbeddingOperator
from datetime import datetime

with DAG(
    dag_id='ovh_ai_embedding_example',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    
    embed_task = OVHCloudAIEndpointsEmbeddingOperator(
        task_id='create_embeddings',
        model='BGE-M3',
        input=[
            "Apache Airflow is a workflow orchestration tool",
            "OVHcloud provides cloud computing services"
        ],
    )
```

#### Using the Hook Directly

```python
from apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints import OVHCloudAIEndpointsHook

def my_custom_function(**context):
    hook = OVHCloudAIEndpointsHook(ovh_conn_id='ovh_ai_endpoints_default')
    
    # Chat completion
    response = hook.chat_completion(
        model='gpt-oss-120b',
        messages=[{"role": "user", "content": "Hello!"}],
        temperature=0.8,
    )
    
    print(response['choices'][0]['message']['content'])
    
    # Create embeddings
    embeddings = hook.create_embedding(
        model='BGE-M3',
        input="Text to embed"
    )
    
    print(embeddings['data'][0]['embedding'])
```

#### Dynamic Templating

Operators support Jinja templating for dynamic values:

```python
from airflow import DAG
from apache_airflow_provider_ovhcloud_ai.operators.ovhcloud_ai import OVHCloudAIEndpointsChatCompletionsOperator
from datetime import datetime

with DAG(
    dag_id='ovh_ai_templating_example',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    
    chat_task = OVHCloudAIEndpointsChatCompletionsOperator(
        task_id='templated_chat',
        model='{{ var.value.llm_model }}',  # From Airflow Variables
        messages=[
            {
                "role": "user", 
                "content": "Process data from {{ ds }}"  # Execution date
            }
        ],
    )
```

### API Reference

### OVHCloudAIEndpointsChatCompletionsOperator

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | str | Required | Model name (e.g., 'gpt-oss-120b') |
| `messages` | List[Dict] | Required | Chat messages with 'role' and 'content' |
| `ovh_conn_id` | str | 'ovh_ai_endpoints_default' | Airflow connection ID |
| `temperature` | float | 1.0 | Sampling temperature (0-2) |
| `max_tokens` | int | None | Maximum tokens to generate |
| `top_p` | float | None | Nucleus sampling parameter |
| `stop` | str/List[str] | None | Stop sequences |
| `user` | str | None | User identifier |

### OVHCloudAIEndpointsEmbeddingOperator

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | str | Required | Embedding model name |
| `input` | str/List[str] | Required | Text(s) to embed |
| `ovh_conn_id` | str | 'ovh_ai_endpoints_default' | Airflow connection ID |
| `user` | str | None | User identifier |

### Available Models

Refer to the [OVHcloud AI Endpoints catalog](https://endpoints.ai.cloud.ovh.net/catalog/) for the latest list of available models.

Common models include:
- **Chat**: gpt-oss-120b, Meta-Llama-3_3-70B-Instruct, etc.
- **Embeddings**: bge-multilingual-gemma2, BGE-M3, etc.

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/ovh/apache-airflow-provider-ovhcloud-ai.git
cd apache-airflow-provider-ovhcloud-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black apache_airflow_provider_ovhcloud_ai/
flake8 apache_airflow_provider_ovhcloud_ai/
mypy apache_airflow_provider_ovhcloud_ai/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/ovh/apache-airflow-provider-ovhcloud-ai#readme)
- 🐛 [Issue Tracker](https://github.com/ovh/apache-airflow-provider-ovhcloud-ai/issues)
- 💬 [Discussions](https://github.com/ovh/apache-airflow-provider-ovhcloud-ai/discussions)

## Acknowledgments

- Built for [Apache Airflow](https://airflow.apache.org/)
- Integrates with [OVHcloud AI Endpoints](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/)