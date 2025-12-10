# SPDX-License-Identifier: Apache-2.0
__all__ = [
    "OVHCloudAIEndpointsHook",
    "OVHCloudAITrainingHook",
]


def __getattr__(name: str):
    if name == "OVHCloudAIEndpointsHook":
        from apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints import OVHCloudAIEndpointsHook
        return OVHCloudAIEndpointsHook
    elif name == "OVHCloudAITrainingHook":
        from apache_airflow_provider_ovhcloud_ai.hooks.ai_training import OVHCloudAITrainingHook
        return OVHCloudAITrainingHook
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


