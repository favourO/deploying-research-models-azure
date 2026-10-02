"""Public Azure Container Apps runtime for the research analysis service."""

from collections.abc import Mapping
from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5

import pulumi
from pulumi_azure_native import app, authorization, managedidentity

ACR_PULL_ROLE_ID = "7f951dda-4ed3-4680-a7ca-43fe172d538d"
CONTAINER_APPS_CONTRIBUTOR_ROLE_ID = "358470bc-b998-42bd-ab17-a7e34c199c0f"


@dataclass(frozen=True)
class RuntimeArgs:
    resource_group_name: pulumi.Input[str]
    location: pulumi.Input[str]
    registry_id: pulumi.Input[str]
    registry_server: pulumi.Input[str]
    github_deployment_principal_id: pulumi.Input[str]
    tags: pulumi.Input[Mapping[str, pulumi.Input[str]]]


class Runtime(pulumi.ComponentResource):
    """A scale-to-zero HTTPS API and web UI backed by a private ACR image."""

    url: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        args: RuntimeArgs,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__("research-analysis:azure:Runtime", name, None, opts)

        environment = app.ManagedEnvironment(
            "container-environment",
            environment_name="research-analysis-dev-env",
            resource_group_name=args.resource_group_name,
            location=args.location,
            public_network_access=app.PublicNetworkAccess.ENABLED,
            tags=args.tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        pull_identity = managedidentity.UserAssignedIdentity(
            "container-pull-identity",
            resource_name_="research-analysis-dev-pull",
            resource_group_name=args.resource_group_name,
            location=args.location,
            tags=args.tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        role_definition_prefix = pulumi.Output.from_input(args.registry_id).apply(
            lambda resource_id: resource_id.split("/resourceGroups/")[0]
        )
        acr_pull = authorization.RoleAssignment(
            "container-acr-pull",
            role_assignment_name=str(
                uuid5(NAMESPACE_URL, "research-analysis-dev-container-acr-pull")
            ),
            principal_id=pull_identity.principal_id,
            principal_type=authorization.PrincipalType.SERVICE_PRINCIPAL,
            role_definition_id=role_definition_prefix.apply(
                lambda prefix: (
                    f"{prefix}/providers/Microsoft.Authorization/roleDefinitions/"
                    f"{ACR_PULL_ROLE_ID}"
                )
            ),
            scope=args.registry_id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        image = pulumi.Output.from_input(args.registry_server).apply(
            lambda server: f"{server}/research-analysis:dev"
        )
        container_app = app.ContainerApp(
            "container-app",
            container_app_name="research-analysis-dev",
            resource_group_name=args.resource_group_name,
            location=args.location,
            environment_id=environment.id,
            identity=app.ManagedServiceIdentityArgs(
                type=app.ManagedServiceIdentityType.USER_ASSIGNED,
                user_assigned_identities=[pull_identity.id],
            ),
            configuration=app.ConfigurationArgs(
                active_revisions_mode=app.ActiveRevisionsMode.SINGLE,
                ingress=app.IngressArgs(
                    external=True,
                    allow_insecure=False,
                    target_port=8000,
                    transport=app.IngressTransportMethod.AUTO,
                ),
                registries=[
                    app.RegistryCredentialsArgs(
                        server=args.registry_server,
                        identity=pull_identity.id,
                    )
                ],
            ),
            template=app.TemplateArgs(
                containers=[
                    app.ContainerArgs(
                        name="research-analysis",
                        image=image,
                        resources=app.ContainerResourcesArgs(cpu=0.25, memory="0.5Gi"),
                    )
                ],
                scale=app.ScaleArgs(min_replicas=0, max_replicas=1),
            ),
            tags=args.tags,
            opts=pulumi.ResourceOptions(parent=self, depends_on=[acr_pull]),
        )

        authorization.RoleAssignment(
            "github-container-app-deploy",
            role_assignment_name=str(
                uuid5(
                    NAMESPACE_URL, "research-analysis-dev-github-container-app-deploy"
                )
            ),
            principal_id=args.github_deployment_principal_id,
            principal_type=authorization.PrincipalType.SERVICE_PRINCIPAL,
            role_definition_id=role_definition_prefix.apply(
                lambda prefix: (
                    f"{prefix}/providers/Microsoft.Authorization/roleDefinitions/"
                    f"{CONTAINER_APPS_CONTRIBUTOR_ROLE_ID}"
                )
            ),
            scope=container_app.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.url = container_app.latest_revision_fqdn.apply(
            lambda fqdn: f"https://{fqdn}"
        )
        self.register_outputs({"url": self.url})
