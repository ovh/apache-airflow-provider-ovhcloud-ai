from typing import Any, Dict, List, Optional, Union
from airflow.models import BaseOperator
from apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints import OVHCloudAIEndpointsHook

class OVHCloudAIEndpointsChatCompletionsOperator(BaseOperator):
    """
    Operator to perform chat completion with OVHcloud AI Endpoints.
    
    :param model: Model name to use
    :param messages: List of message objects with 'role' and 'content'
    :param ovh_conn_id: Connection ID for OVHcloud AI Endpoints
    :param temperature: Sampling temperature (0-2)
    :param max_tokens: Maximum tokens to generate
    :param top_p: Nucleus sampling parameter
    :param stop: Stop sequences
    
    Example:
        .. code-block:: python
        
            chat_task = OVHCloudAIEndpointsChatCompletionsOperator(
                task_id='chat_completion',
                model='gpt-oss-120b',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"}
                ],
                temperature=0.7,
                max_tokens=100
            )
    """
    
    template_fields = ("messages", "model")
    
    def __init__(
        self,
        model: str,
        messages: List[Dict[str, str]],
        ovh_conn_id: str = OVHCloudAIEndpointsHook.default_conn_name,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.model = model
        self.messages = messages
        self.ovh_conn_id = ovh_conn_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stop = stop
        self.stream = stream
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the chat completion request."""
        hook = OVHCloudAIEndpointsHook(ovh_conn_id=self.ovh_conn_id)
        
        response = hook.chat_completion(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            stream=self.stream,
            stop=self.stop,
        )
        
        self.log.info(f"Chat completion successful. Tokens used: {response.get('usage', {})}")
        return response

class OVHCloudAIEndpointsEmbeddingOperator(BaseOperator):
    """
    Operator to create embeddings with OVHcloud AI Endpoints.
    
    :param model: Model name to use for embeddings
    :param input: Text or list of texts to embed
    :param ovh_conn_id: Connection ID for OVHcloud AI Endpoints
    
    Example:
        .. code-block:: python
        
            embed_task = OVHCloudAIEndpointsEmbeddingOperator(
                task_id='create_embedding',
                model='BGE-M3',
                input="Text to embed"
            )
    """
    
    template_fields = ("input", "model")
    
    def __init__(
        self,
        model: str,
        input: Union[str, List[str]],
        ovh_conn_id: str = OVHCloudAIEndpointsHook.default_conn_name,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.model = model
        self.input = input
        self.ovh_conn_id = ovh_conn_id
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the embedding request."""
        hook = OVHCloudAIEndpointsHook(ovh_conn_id=self.ovh_conn_id)
        
        response = hook.create_embedding(
            model=self.model,
            input=self.input,
        )
        
        self.log.info(f"Embedding created successfully. Total tokens: {response.get('usage', {}).get('total_tokens')}")
        return response

