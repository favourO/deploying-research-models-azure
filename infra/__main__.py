"""Composition root for Azure infrastructure."""

from hashlib import sha256

import pulumi
from pulumi_azure_native import resources

from components.registry import Registry, RegistryArgs
from components.runtime import Runtime, RuntimeArgs
from components.storage import Storage, StorageArgs

config = pulumi.Config()
environment = config.require("environment")
location = config.require("location")
allowed_environments = {"dev", "staging", "prod"}

if environment not in allowed_environments:
    raise ValueError("environment must be one of: dev, staging, prod")

if pulumi.get_stack() != environment:
    raise ValueError(
        f"Selected stack '{pulumi.get_stack()}' does not match configured "
        f"environment '{environment}'."
    )

project_name = "research-analysis-platform"
tags = {
    "project": project_name,
    "environment": environment,
    "managed-by": "pulumi",
    "service": "research-analysis",
}

resource_group = resources.ResourceGroup(
    "resource-group",
    resource_group_name=f"research-analysis-{environment}-rg",
    location=location,
    tags=tags,
)

# Azure Storage names are global, 3–24 lowercase alphanumeric characters. This
# stable project/stack hash keeps names repeatable without a random resource.
suffix = sha256(f"{pulumi.get_project()}-{pulumi.get_stack()}".encode()).hexdigest()[:8]
generated_storage_account_name = f"research{environment}{suffix}"
generated_registry_name = f"researchanalysis{environment}{suffix}"

platform_storage = Storage(
    "storage",
    StorageArgs(
        account_name=generated_storage_account_name,
        resource_group_name=resource_group.name,
        location=resource_group.location,
        tags=tags,
    ),
)

platform_registry = Registry(
    "registry",
    RegistryArgs(
        registry_name=generated_registry_name,
        resource_group_name=resource_group.name,
        location=resource_group.location,
        tags=tags,
    ),
)

runtime = Runtime(
    "runtime",
    RuntimeArgs(
        resource_group_name=resource_group.name,
        location=resource_group.location,
        registry_id=platform_registry.registry_id,
        registry_server=platform_registry.registry_login_server,
        github_deployment_principal_id=config.require("githubDeploymentPrincipalId"),
        tags=tags,
    ),
)

pulumi.export("environment", environment)
pulumi.export("location", location)
pulumi.export("resourceGroupName", resource_group.name)
pulumi.export("resourceGroupId", resource_group.id)
pulumi.export("storageAccountName", platform_storage.storage_account_name)
pulumi.export("datasetsContainerName", platform_storage.datasets_container_name)
pulumi.export("resultsContainerName", platform_storage.results_container_name)
pulumi.export("registryName", platform_registry.registry_name)
pulumi.export("registryLoginServer", platform_registry.registry_login_server)
pulumi.export("applicationUrl", runtime.url)
