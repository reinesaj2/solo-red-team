# Lab Sandbox

This sandbox runs intentionally vulnerable demo endpoints locally for safe testing.

- Services:
  - Basic auth demo on port 8081
  - Digest auth demo on port 8082
  - HTML form demo on port 8083

## How to run safely

1. Ensure Docker Desktop is running.
2. Prefer running offline or on a private network (Airplane Mode recommended).
3. Start the lab:
```bash
docker compose -f lab/docker-compose.yml up -d
```
4. Stop the lab:
```bash
docker compose -f lab/docker-compose.yml down -v
```

Never point tools at live targets. This environment is for education only.
