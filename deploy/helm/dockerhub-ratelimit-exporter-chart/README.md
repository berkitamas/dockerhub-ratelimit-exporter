# dockerhub-ratelimit-exporter-chart

![Version: 1.0.2](https://img.shields.io/badge/Version-1.0.2-informational?style=flat-square)

Prometheus exporter for Docker Hub rate limits

## Installation
Using values from a file:

```bash
helm install -f values.yaml `HELM_RELEASE_NAME` . -n `NAMESPACE`
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| dockerHubCredentials.existingSecret | string | `nil` |  |
| dockerHubCredentials.password | string | `nil` |  |
| dockerHubCredentials.username | string | `nil` |  |
| extraAnnotations | object | `{}` |  |
| extraEnvFrom | list | `[]` |  |
| extraEnvVars | list | `[]` |  |
| extraLabels | object | `{}` |  |
| extraVolumeMounts | list | `[]` |  |
| extraVolumes | list | `[]` |  |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"berkitamas/dockerhub-ratelimit-exporter"` |  |
| image.tag | string | `""` |  |
| imagePullSecrets | list | `[]` |  |
| initContainers | list | `[]` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| service.port | int | `8000` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| serviceMonitor.enabled | bool | `false` |  |
| serviceMonitor.interval | string | `nil` |  |
| serviceMonitor.metricRelabelings | object | `{}` |  |
| serviceMonitor.relabelings | object | `{}` |  |
| tolerations | list | `[]` |  |
