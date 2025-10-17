# Deployment Guilde

- [Dependencies](#dependencies)
- [Helm](#helm-repository)


## Dependencies

- An existing Kubernetes cluster, version 1.26 or greater.
- A working [`base` Helm Chart](https://github.com/opencadc/science-platform/tree/main/deployment/helm#base-install) install.  If using Traefik, add a port (entry point) that this SSHD service will expose, which will be declared in the `traefik.ports` section.  Example:
  ```yaml
  # Install Traefik by default.  Set to true to add it in.  Omitting it defaults to true, so beware.
  traefik:
    install: true
    ports:
      sshd:
        port: 64022  # Expose port 64022.
        expose: true
  ```
- A `PersistentVolumeClaim` claiming storage that contains the root of the User Storage.  This will be the same `PersistentVolumeClaim` that Cavern uses (if installed).  See
- A Kubernetes secret called `sssd-ldap-secret` in the Skaha Namespace (defaults to `skaha-system`) with a single key of `ldap-password` whose value is the password of the LDAP bind user as configured in the `values.yaml` file for (`deployment.sshd.ldap.bindDN`):
  - `kubectl -n skaha-system create secret generic sssd-ldap-secret --from-literal="ldap-password=my-super-secret-passwd"`

## Sample Values file

```yaml
deployment:
  sshd:
    entryPoint: sshd
    rootPath: "/cavern"  # If Cavern is installed, this will point to the same location as deployment.cavern.filesystem.subPath.

    # LDAP configuration information.  Authentication is handled by the secret/sssd.conf file.
    ldap:
      url: "ldaps://my-ldap-host.example.org"
      searchBase: "dc=exmaple,dc=org"
      userSearchBase: "ou=users,ou=ds,dc=example,dc=org"
      groupSearchBase: "ou=groups,ou=ds,dc=example,dc=org"
      bindDN: "uid=superuser,ou=Admins,dc=example,dc=org"

storage:
  service:
    spec:
      persistentVolumeClaim:
        claimName: skaha-pvc # Match this label up with whatever was installed in the base install, or the desired PVC, or create dynamically provisioned storage.

```
