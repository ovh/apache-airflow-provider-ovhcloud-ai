# SPDX-License-Identifier: Apache-2.0
from typing import Any, Dict, List, Optional, Union
import requests
from airflow.sdk.bases.hook import BaseHook
from airflow.exceptions import AirflowException

class OVHCloudAIEndpointsHook(BaseHook):
    """
    Hook to interact with OVHcloud AI Endpoints API.
    
    This hook provides methods to interact with OVHcloud AI Endpoints provider,
    which follows the OpenAI API specification.
    
    :param ovh_conn_id: Connection ID for OVHcloud AI Endpoints
    :param timeout: Request timeout in seconds
    
    Example connection configuration:
        - Conn Id: ovh_ai_endpoints_default
        - Conn Type: generic
        - Password: your-api-key
    """
    
    conn_name_attr = "ovh_conn_id"
    default_conn_name = "ovh_ai_endpoints_default"
    conn_type = "ai_endpoints"
    hook_name = "OVHcloud AI Endpoints"
    
    BASE_URL = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"
    
    def __init__(
        self,
        ovh_conn_id: str = default_conn_name,
        timeout: int = 60,
    ) -> None:
        super().__init__()
        self.ovh_conn_id = ovh_conn_id
        self.timeout = timeout
        self._api_key = None
        
    def get_conn(self) -> str:
        """Get the API key from Airflow connection."""
        if self._api_key is None:
            conn = self.get_connection(self.ovh_conn_id)
            self._api_key = conn.password or conn.get_extra().get('api_key')
            
            if not self._api_key:
                raise AirflowException(
                    f"OVHcloud AI Endpoints API key not found in connection '{self.ovh_conn_id}'. "
                    "Please set it in the password field or extra field as 'api_key'."
                )
        return self._api_key
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization."""
        api_key = self.get_conn()
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to OVHcloud AI Endpoints API."""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise AirflowException(f"Request to OVHcloud AI Endpoints failed: {str(e)}")
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a chat completion using OVHcloud AI Endpoints.
        
        :param model: Model name to use
        :param messages: List of message objects with 'role' and 'content'
        :param temperature: Sampling temperature (0-2)
        :param max_tokens: Maximum tokens to generate
        :param top_p: Nucleus sampling parameter
        :param stream: Whether to stream responses
        :param stop: Stop sequences
        :param kwargs: Additional parameters
        :return: API response
        """
        data = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if stop is not None:
            data["stop"] = stop
        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p
            
        data.update(kwargs)
        
        self.log.info(f"Sending chat completion request with model: {model}")
        return self._make_request("POST", "chat/completions", data)
    
    def create_embedding(
        self,
        model: str,
        input: Union[str, List[str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create embeddings using OVHcloud AI Endpoints.
        
        :param model: Model name to use
        :param input: Text or list of texts to embed
        :param kwargs: Additional parameters
        :return: API response with embeddings
        """
        data = {
            "model": model,
            "input": input,
        }
                    
        data.update(kwargs)
        
        self.log.info(f"Sending embedding request with model: {model}")
        return self._make_request("POST", "embeddings", data)
    
    def test_connection(self) -> tuple[bool, str]:
        """Test the connection to OVHcloud AI Endpoints."""
        try:
            self.get_conn()
            return True, "Connection successfully tested"
        except Exception as e:
            return False, str(e)