# Repository retirement

- Requested by the owner on 2026-10-13.
- End state: decommissioned, preserved as an archived reference.
- The project remained a pre-implementation model lab; no production API or
  web application was deployed from this repository.
- Source, simulation scenarios, refined invariants, evaluation records,
  history, and license are preserved.
- No open GitHub issues or pull requests remained at retirement.

## Verified surfaces

- No deployment configuration or GitHub Actions workflows exist.
- GitHub Pages is not configured (Pages API returned 404).
- No other local process with this repository as its working directory was
  found during retirement.
- No Vila deployment contract or stack file exists in infra-platform.
- AWS account `590183855481`, region `us-east-1`, has no Vila ECR repository.
- SSM command `8c0c281c-03b7-47fe-b172-6c646d9a8c7c` succeeded on
  manager `i-005c1410ca6db07b6` and worker `i-059021330bdc8ccac`;
  stack, service, and running-container inventories contain no Vila runtime.

GitHub Actions is disabled at archival. No deployed runtime required removal.
