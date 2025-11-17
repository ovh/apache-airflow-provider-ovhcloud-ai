# SPDX-License-Identifier: Apache-2.0
__version__ = "1.0.0"

def get_provider_info():
    return {
        "package-name": "apache-airflow-provider-ovhcloud-ai",
        "name": "OVHcloud AI",
        "description": "Apache Airflow Provider for OVHcloud AI",
        "versions": [__version__],
        "connection-types": [
            {
                "connection-type": "ai_endpoints",
                "hook-class-name": "apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints.OVHCloudAIEndpointsHook",
            }
        ],
        "hook-class-names": [
            "apache_airflow_provider_ovhcloud_ai.hooks.ai_endpoints.OVHCloudAIEndpointsHook"
        ],
        "extra-links": [],
    }
