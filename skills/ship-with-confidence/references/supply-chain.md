# Software supply-chain gate

Scale this gate to exposure, with mandatory depth for CI/CD, releases, containers, infrastructure, package publishing, or security-sensitive dependencies.

- Use locked, reproducible dependency resolution and review install/build scripts, new transitive dependencies, licenses, maintainers, and provenance.
- Generate an SBOM for release artifacts when supported; scan the artifact actually shipped, not only source manifests.
- Pin third-party CI actions and build images to immutable digests/commit SHAs; isolate secrets and minimize token permissions.
- Produce build provenance and signatures/attestations where the release system supports them; verify them at promotion/deploy boundaries.
- Run dependency, secret, SAST, container, and IaC checks appropriate to the stack. Triage findings rather than treating scanner silence as proof.
- Record update policy, owner, emergency revocation/rollback, and handling for abandoned or compromised dependencies.

Prefer OpenSSF Scorecard/SLSA concepts and repository-native tooling. Do not install an attractive GitHub tool solely by star count; pin, license-check, inspect scripts/network behavior, and prove value on a disposable fixture first.
