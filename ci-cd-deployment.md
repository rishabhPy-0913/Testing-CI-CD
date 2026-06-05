# GitHub-Based CI/CD and Deployment Strategy

## Overview

This document outlines the standard deployment process for all services and applications managed through GitHub. The objective is to establish a consistent, automated, and secure deployment workflow while maintaining rollback capabilities and environment-specific deployment configurations.

## CI/CD Pipeline

Every repository will maintain its own CI/CD pipeline using GitHub Actions. The pipeline will be responsible for building, packaging, and publishing deployable artifacts whenever changes are merged into the designated branches.

Key responsibilities of the pipeline include:

* Source code checkout and validation.
* Execution of automated tests and quality checks.
* Docker image creation for the application.
* Publishing Docker images to the Azure Container Registry (ACR).
* Triggering deployment workflows where applicable.

This approach ensures that all repositories follow a standardized deployment process while allowing teams to maintain service-specific build logic.

## Docker Image Management

Each repository will produce a Docker image as part of the CI/CD process.

The image lifecycle will follow the versioning strategy below:

* Every successful build will generate a versioned image tag (for example: `v1.2.0`, `v2026.06.03.1`, or a commit-based version).
* The newly built image will also be tagged as `latest`.
* The previous deployment image will remain preserved using its version-specific tag.
* The `latest` tag will always represent the most recently approved build available for deployment.

This strategy allows environments to consume the most recent release while retaining historical versions for rollback purposes.

## GitHub Hosted Runner Security and Build Environment

Docker image builds will be performed on GitHub-hosted runners.

During execution:

* GitHub creates a temporary virtual machine (VM) for the workflow.
* The repository source code and workflow definitions (`.github/workflows/*.yml`) are copied to the runner.
* Build, test, and Docker image creation activities occur on the temporary runner.
* Once the workflow completes, the runner VM is automatically destroyed.

GitHub-hosted runners are ephemeral by design and are cleaned after every job execution. As a result, no repository code, build artifacts, or deployment data remain on the runner after the workflow finishes.

## Environment Configuration Repository

A dedicated repository will be maintained to manage deployment configurations and environment-specific infrastructure artifacts.

This repository will contain:

* Docker Compose files for each environment (Development, QA, UAT, Production, etc.).
* Environment-specific deployment scripts.
* Deployment automation utilities.
* Infrastructure configuration files required for service orchestration.

Deployment servers will pull configurations from this repository and use Docker Compose to deploy services.

Each Compose file will reference the latest approved image from ACR for the corresponding service.

### Future Enhancements

As the platform grows, deployment configurations may be organized further through:

* Product-specific Docker Compose files.
* Team-specific deployment stacks.
* Modular deployment definitions for independent services and business domains.

## Deployment Process

The deployment workflow will follow the sequence below:

1. Developer merges code changes into the target branch.
2. GitHub Actions pipeline is triggered.
3. Docker image is built on a GitHub-hosted runner.
4. Image is pushed to Azure Container Registry (ACR).
5. Image is tagged with both:

   * A unique version tag.
   * The `latest` tag.
6. Deployment server retrieves the updated configuration from the deployment repository.
7. Docker Compose pulls the latest image from ACR.
8. Services are deployed or updated on the target environment.

## Rollback and Failure Recovery Strategy

To minimize downtime and deployment risk, a rollback mechanism will be maintained.

If a deployment fails due to application startup issues, health check failures, or runtime errors:

1. The failed deployment will be identified and stopped.
2. The previously deployed stable image version will be selected.
3. Docker Compose will be updated to reference the previous version.
4. The service will be redeployed using the last known stable image.

This approach ensures rapid recovery while root-cause analysis and fixes are performed on the failed release.

## Benefits

* Standardized deployment process across all repositories.
* Automated image creation and publishing.
* Secure and isolated build environments using GitHub-hosted runners.
* Centralized management of environment configurations.
* Consistent deployment methodology across teams.
* Version-controlled rollback capability.
* Improved operational reliability and deployment traceability.
