"""Azure Container Registry component for application artifacts."""

from collections.abc import Mapping
from dataclasses import dataclass

import pulumi
from pulumi_azure_native import containerregistry


@dataclass(frozen=True)
class RegistryArgs:
    resource_group_name: pulumi.Input[str]
    location: pulumi.Input[str]
    registry_name: pulumi.Input[str]
    tags: pulumi.Input[Mapping[str, pulumi.Input[str]]]


class Registry(pulumi.ComponentResource):
    """A cost-conscious registry with Entra/RBAC authentication only."""

    registry_name: pulumi.Output[str]
    registry_login_server: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        args: RegistryArgs,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__("research-analysis:azure:Registry", name, None, opts)

        registry = containerregistry.Registry(
            "registry",
            registry_name=args.registry_name,
            resource_group_name=args.resource_group_name,
            location=args.location,
            sku=containerregistry.SkuArgs(name=containerregistry.SkuName.BASIC),
            admin_user_enabled=False,
            anonymous_pull_enabled=False,
            public_network_access=containerregistry.PublicNetworkAccess.ENABLED,
            tags=args.tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.registry_name = registry.name
        self.registry_login_server = registry.login_server

        self.register_outputs(
            {
                "registryName": self.registry_name,
                "registryLoginServer": self.registry_login_server,
            }
        )
