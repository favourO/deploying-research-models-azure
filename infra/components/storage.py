"""Azure Blob Storage component for research datasets and results."""

from collections.abc import Mapping
from dataclasses import dataclass

import pulumi
from pulumi_azure_native import storage


@dataclass(frozen=True)
class StorageArgs:
    resource_group_name: pulumi.Input[str]
    location: pulumi.Input[str]
    account_name: pulumi.Input[str]
    tags: pulumi.Input[Mapping[str, pulumi.Input[str]]]


class Storage(pulumi.ComponentResource):
    """Storage used for research inputs and generated analysis results."""

    storage_account_name: pulumi.Output[str]
    datasets_container_name: pulumi.Output[str]
    results_container_name: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        args: StorageArgs,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__("research-analysis:azure:Storage", name, None, opts)

        account = storage.StorageAccount(
            "account",
            account_name=args.account_name,
            resource_group_name=args.resource_group_name,
            location=args.location,
            kind=storage.Kind.STORAGE_V2,
            sku=storage.SkuArgs(name=storage.SkuName.STANDARD_LRS),
            access_tier=storage.AccessTier.HOT,
            allow_blob_public_access=False,
            allow_cross_tenant_replication=False,
            enable_https_traffic_only=True,
            encryption=storage.EncryptionArgs(
                key_source=storage.KeySource.MICROSOFT_STORAGE,
                services=storage.EncryptionServicesArgs(
                    blob=storage.EncryptionServiceArgs(
                        enabled=True,
                        key_type=storage.KeyType.ACCOUNT,
                    ),
                    file=storage.EncryptionServiceArgs(
                        enabled=True,
                        key_type=storage.KeyType.ACCOUNT,
                    ),
                ),
            ),
            minimum_tls_version=storage.MinimumTlsVersion.TLS1_2,
            network_rule_set=storage.NetworkRuleSetArgs(
                bypass=storage.Bypass.NONE,
                default_action=storage.DefaultAction.ALLOW,
            ),
            public_network_access=storage.PublicNetworkAccess.ENABLED,
            tags=args.tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        datasets = storage.BlobContainer(
            "datasets",
            account_name=account.name,
            container_name="datasets",
            default_encryption_scope="$account-encryption-key",
            deny_encryption_scope_override=False,
            public_access=storage.PublicAccess.NONE,
            resource_group_name=args.resource_group_name,
            opts=pulumi.ResourceOptions(parent=self),
        )

        results = storage.BlobContainer(
            "results",
            account_name=account.name,
            container_name="results",
            default_encryption_scope="$account-encryption-key",
            deny_encryption_scope_override=False,
            public_access=storage.PublicAccess.NONE,
            resource_group_name=args.resource_group_name,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.storage_account_name = account.name
        self.datasets_container_name = datasets.name
        self.results_container_name = results.name

        self.register_outputs(
            {
                "storageAccountName": self.storage_account_name,
                "datasetsContainerName": self.datasets_container_name,
                "resultsContainerName": self.results_container_name,
            }
        )
