# SPDX-License-Identifier: Apache-2.0
__all__ = [
    # AI Endpoints
    "OVHCloudAIEndpointsChatCompletionsOperator",
    "OVHCloudAIEndpointsEmbeddingOperator",
    # AI Training
    "OVHCloudAITrainingSubmitJobOperator",
    "OVHCloudAITrainingGetJobOperator",
    "OVHCloudAITrainingStopJobOperator",
    "OVHCloudAITrainingDeleteJobOperator",
    "OVHCloudAITrainingGetLogsOperator",
    "OVHCloudAITrainingWaitForJobOperator",
]


def __getattr__(name: str):
    if name in ("OVHCloudAIEndpointsChatCompletionsOperator", "OVHCloudAIEndpointsEmbeddingOperator"):
        from apache_airflow_provider_ovhcloud_ai.operators import ai_endpoints
        return getattr(ai_endpoints, name)
    elif name in (
        "OVHCloudAITrainingSubmitJobOperator",
        "OVHCloudAITrainingGetJobOperator",
        "OVHCloudAITrainingStopJobOperator",
        "OVHCloudAITrainingDeleteJobOperator",
        "OVHCloudAITrainingGetLogsOperator",
        "OVHCloudAITrainingWaitForJobOperator",
    ):
        from apache_airflow_provider_ovhcloud_ai.operators import ai_training
        return getattr(ai_training, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


