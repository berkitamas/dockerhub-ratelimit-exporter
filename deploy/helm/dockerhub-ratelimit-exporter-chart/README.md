# dockerhub-ratelimit-exporter-chart

![Version: 1.0.4](https://img.shields.io/badge/Version-1.0.4-informational?style=flat-square)

Prometheus exporter for Docker Hub rate limits

## Installation
Using values from a file:

```bash
helm install -f values.yaml `HELM_RELEASE_NAME` . -n `NAMESPACE`
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` | Affinity rules for the Pod |
| dockerHubCredentials.existingSecret | string | `nil` | Existing secret where the credentials are retrieved (must have username and password key) |
| dockerHubCredentials.password | string | `nil` | Password/Token of Docker Hub user (mutually exclusive with existingSecret) |
| dockerHubCredentials.username | string | `nil` | Username of Docker Hub user (mutually exclusive with existingSecret) |
| extraAnnotations | object | `{}` | Extra annotations for the Deployment |
| extraArgs | list | `[]` | Extra arguments for the container |
| extraEnvFrom | list | `[]` | Extra environment variable mounts for the container |
| extraEnvVars | list | `[]` | Extra environment variables for the container |
| extraLabels | object | `{}` | Extra labels for the Deployment |
| extraVolumeMounts | list | `[]` | Extra volume mounts for the container |
| extraVolumes | list | `[]` | Extra volumes for the container |
| fullnameOverride | string | `""` | Overrides the full name of the resources (by default it is prepended by the chart name) |
| image.pullPolicy | string | `"IfNotPresent"` | Image Pull Policy of the image |
| image.repository | string | `"berkitamas/dockerhub-ratelimit-exporter"` | Repository of the image |
| image.tag | string | `""` | Overrides the image tag whose default is the chart appVersion. |
| imagePullSecrets | list | `[]` | Image Pull Secrets of the image |
| initContainers | list | `[]` | Extra init containers for the container |
| nameOverride | string | `""` | Overrides the name of the chart |
| nodeSelector | object | `{}` | Node selector for the Pod |
| podSecurityContext | object | `{}` | Security context of the pod |
| replicaCount | int | `1` | Number of replicas |
| resources | object | `{}` | Resources of the Pod |
| securityContext | object | `{}` | Security context of the container |
| service.port | int | `8000` | Service port (should align with the arguments) |
| service.type | string | `"ClusterIP"` | Service type |
| serviceAccount.annotations | object | `{}` | Annotations to add to the service account |
| serviceAccount.create | bool | `true` | Specifies whether a service account should be created |
| serviceAccount.name | string | `""` | The name of the service account to use. If not set and create is true, a name is generated using the fullname template. |
| serviceMonitor.enabled | bool | `false` | Whether enable the serviceMonitor |
| serviceMonitor.interval | string | `nil` | Prometheus scrape interval |
| serviceMonitor.metricRelabelings | object | `{}` | Prometheus metric relabelings |
| serviceMonitor.relabelings | object | `{}` | Prometheus relabelings |
| tolerations | list | `[]` | Tolerations for the Pod |
