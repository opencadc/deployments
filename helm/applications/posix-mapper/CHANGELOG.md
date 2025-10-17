# CHANGELOG for POSIX Mapper (0.5.0)

## 2025.07.28 (0.5.0)
### 🚨 Breaking Changes
- 🛑 🔥 Removed default PostgreSQL database.  It is expected that deployers will run their own PostreSQL database with permanent storage.

## 2025.07.16 (0.4.4)
- Fix for default GID with new Users.  Default GID will match new User's UID.

## 2025.04.15 (0.4.1)
- Add `tolerations` feature for `posix-mapper` API and supprting PostgreSQL deployment.
  - See https://github.com/opencadc/deployments/issues/29

## 2025.02.11 (0.4.0)
- Rework fix of memory leak by properly closing the Hibernate SessionFactory
- Removed default `hostPath` in storage spec of postgresql database

## 2025.01.24 (0.3.0)
- Fix memory leak in POSIX Mapper application

## 2024.12.19 (0.2.1)
- Make postgresql configurable for external databases

## 2024.12.11 (0.2.0)
- Added support for `securityContext`
- Added support to rename application to change endpoint
- Small fixes and error reporting

## 2023.11.02 (0.1.8)
- Swagger documentation fix (Bug)
- Properly authenticate Bearer tokens (Improvement)
- Now supports setting the `gmsID` and `oidcURI` configurations (was hard-coded to SKAO)
- Code cleanup
