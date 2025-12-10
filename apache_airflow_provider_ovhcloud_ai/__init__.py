# SPDX-License-Identifier: Apache-2.0
__version__ = "1.0.0"

def get_provider_info():
    return {
        "package-name": "apache-airflow-provider-ovhcloud-ai",
        "name": "OVHcloud AI",
        "description": "Apache Airflow Provider for OVHcloud AI (AI Endpoints & AI Training)",
        "versions": [__version__],
        "connection-types": [
            {
                "connection-type": "ai_endpoints",
                "hook-class-name": "apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints.OVHCloudAIEndpointsHook",
            },
            {
                "connection-type": "ai_training",
                "hook-class-name": "apache_airflow_provider_ovhcloud_ai.hooks.ai_training.OVHCloudAITrainingHook",
            },
        ],
        "hook-class-names": [
            "apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints.OVHCloudAIEndpointsHook",
            "apache_airflow_provider_ovhcloud_ai.hooks.ai_training.OVHCloudAITrainingHook",
        ],
        "extra-links": [],
    }
