# Helm Chart for the Cavern User Storage API

See the [Deployment Guide](../README.md) for a better idea of a full system.

## Install

This `README` will focus on a basic install using a new `values-local.yaml` file.

A working Science Platform is not required, but the Persistent Volume Claims are needed.  Those PVs and PVCs will
provide the underlying storage for the Services and User Sessions.

### From source

Installation depends on a working Kubernetes cluster version 1.23 or greater.

The base install also installs the Traefik proxy, which is needed by the Ingress when the Science Platform services are installed.

```sh
$ git clone https://github.com/opencadc/science-platform.git
$ cd science-platform/deployment/helm
$ helm install -n skaha-system --dependency-update --values my-values-local.yaml <name> ./cavern
```

Where `<name>` is the name of this installation.  Example:
```sh
$ helm install -n skaha-system --dependency-update --values my-values-local.yaml cavern ./cavern
```
This will install Skaha service dependency, as well as the Skaha webservice and any necessary Ingress.
```
NAME: cavern
LAST DEPLOYED: <Timestamp e.g. Fri Nov 07 04:19:04 2023>
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

## Verification

After the install, there should exist the necessary Service.  See the Namespaces:

```sh
$ kubectl -n skaha-system get services
NAME                   STATUS   AGE
...
skaha-system   cavern-tomcat-svc             ClusterIP      10.108.202.148   <none>        8080/TCP            1m
```

The [IVOA VOSI availability](https://www.ivoa.net/documents/VOSI/20170524/REC-VOSI-1.1.html#tth_sEc5.5) endpoint can be used to 
check that the Skaha service has started properly.  It may take a few moments to start up.

```sh
$ curl https://myhost.example.com/cavern/availability

<?xml version="1.0" encoding="UTF-8"?>
<vosi:availability xmlns:vosi="http://www.ivoa.net/xml/VOSIAvailability/v1.0">
  <vosi:available>true</vosi:available>
  <vosi:note>service is accepting requests.</vosi:note>
  <!--<clientip>192.1.1.4</clientip>-->
</vosi:availability>
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `kubernetesClusterDomain` | Kubernetes cluster domain used to find internal hosts | `cluster.local` |
| `replicaCount` | Number of Cavern replicas to deploy | `1` |
| `tolerations` | Array of tolerations to pass to Kubernetes for fine-grained Node targeting of the Cavern API | `[]` |
| `deployment.hostname` | Hostname for the Cavern deployment | `""` |
| `deployment.cavern.loggingGroups` | List of groups permitted to adjust logging levels for the Cavern service. | `[]` |
| `deployment.cavern.image` | Cavern Docker image | `images.opencadc.org/platform/cavern:<current release version>` |
| `deployment.cavern.imagePullPolicy` | Image pull policy for the Cavern container | `IfNotPresent` |
| `deployment.cavern.resourceID` | Resource ID (URI) for this Cavern service | `""` |
| `deployment.cavern.oidcURI` | URI (or URL) for the OIDC service | `""` |
| `deployment.cavern.gmsID` | Resource ID (URI) for the IVOA Group Management Service | `""` |
| `deployment.cavern.adminAPIKeys` | API keys for client applications that can create new allocations | `{}` |
| `deployment.cavern.allocations.defaultSizeGB` | Default size of user allocations in GB | `10` |
| `deployment.cavern.allocations.parentFolders` | List of parent folders to create for user allocations.  Best to leave this alone. | `["/home", "/projects"]` |
| `deployment.cavern.filesystem.dataDir` | Persistent data directory in the Cavern container | `""` |
| `deployment.cavern.filesystem.subPath` | Relative path to the node/file content that could be mounted in other containers | `""` |
| `deployment.cavern.filesystem.rootOwner.username` | Username of the root owner of the filesystem data (parent of allocations) directory | `""` |
| `deployment.cavern.filesystem.rootOwner.uid` | UID of the root owner of the filesystem data (parent of allocations) directory | `""` |
| `deployment.cavern.filesystem.rootOwner.gid` | GID of the root owner of the filesystem data (parent of allocations) directory | `""` |
| `deployment.cavern.filesystem.rootOwner.adminUsername` | Admin username for the filesystem data (parent of allocations) directory
| `deployment.cavern.identityManagerClass` | Class name for the identity manager used by Cavern | `org.opencadc.auth.StandardIdentityManager` |
| `deployment.cavern.uws.db.install` | Whether to deploy a local PostgreSQL database for UWS | `true` |
| `deployment.cavern.uws.db.image` | PostgreSQL image to use for UWS | `postgres:15.12` |
| `deployment.cavern.uws.db.runUID` | UID for the PostgreSQL user in the UWS database | `999` |
| `deployment.cavern.uws.db.database` | Name of the UWS database | `uws` |
| `deployment.cavern.uws.db.url` | JDBC URL for the UWS database.  Use instead of `database`. | `jdbc:postgresql://cavern-uws-db:5432/uws` |
| `deployment.cavern.uws.db.username` | Username for the UWS database | `uwsuser` |
| `deployment.cavern.uws.db.password` | Password for the UWS database | `uwspwd` |
| `deployment.cavern.uws.db.schema` | Schema name for the UWS database | `uws` |
| `deployment.cavern.uws.db.maxActive` | Maximum number of active connections to the UWS database | `2` |
| `deployment.applicationName` | Optional rename of the application from the default "cavern" | `cavern` |
| `deployment.endpoint` | Endpoint to serve the Cavern service from | `/cavern` |
| `deployment.extraEnv` | Extra environment variables to set in the Cavern container | `[]` |
| `deployment.extraVolumeMounts` | Extra volume mounts for the Cavern container | `[]` |
| `deployment.extraVolumes` | Extra volumes to mount in the Cavern container | `[]` |
| `deployment.resources.requests.memory` | Memory request for the Cavern container | `1Gi` |
| `deployment.resources.requests.cpu` | CPU request for the Cavern container | `500m` |
| `deployment.resources.limits.memory` | Memory limit for the Cavern container | `1Gi` |
| `deployment.resources.limits.cpu` | CPU limit for the Cavern container | `500m` |
| `tolerations` | Tolerations to apply to the Cavern Pod | `[]` |
| `secrets` | Secrets to create for the Cavern service, such as CA certificates | `{}` |
| `service.cavern.extraPorts` | Extra ports to expose for the Cavern service | `[]` |
| `storage.service.spec` | Storage specification for the Cavern service | `{}` |

## User Allocations with special access
Cavern typically accepts user allocation requests from the Administrative user, but it can be configured to allow other users to request allocations as well. This is done by adding the user's API key to the `deployment.cavern.allocations.apiKeys` configuration:
```yaml
deployment:
  cavern:
    adminAPIKeys:
      skaha: "skahasecretkey1234567890"
      prepareData: "preparedatasecretkey1234567890"
```

With this configuration, listed clients can request new user allocations using the `api-key` challenge type in the `Authorization` header.  This `api-key` represents a trusted client application to act on behalf of the Administrative user:
```sh
$ curl -Lv --header "Authorization: api-key prepareData:preparedatasecretkey1234567890" --header "content-type: text/xml" --upload-file user-alloc-upload-jwt.xml https://example.org/cavern/nodes/home/new-user
```

Where the upload XML file would look like this:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<vos:node xmlns:vos="http://www.ivoa.net/xml/VOSpace/v2.0" 
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
          uri="vos://exmaple.org~cavern/home/new-user" xsi:type="vos:ContainerNode">
  <vos:properties>
    <vos:property uri="ivo://opencadc.org/vospace/core#creatorJWT">JWT_TOKEN_REPLACE_ME</vos:property> <!-- JWT token of the new user -->
    <vos:property uri="ivo://cadc.nrc.ca/vospace/core#inheritPermissions">true</vos:property>
    <vos:property uri="ivo://ivoa.net/vospace/core#quota">524288000</vos:property>. <!-- 500MB quota example, adjust as needed -->
  </vos:properties>
  <vos:nodes />
</vos:node>
```
Where `JWT_TOKEN_REPLACE_ME` is replaced with a valid JWT token of the new user (i.e. the one making the request to be added).  Don't forget to set the `vos:property:uri` to the correct value for your service and the path of the new user.