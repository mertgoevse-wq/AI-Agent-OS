# Security Report
## Overview
RBAC permissions are implemented but tools lack strong execution sandboxes.
## OMNI Upgrade Path
- **Sandboxed Execution:** Python and shell tools must run inside an isolated MicroVM or Docker container to prevent destructive host access.
- **Audit Logging:** Every memory access, tool invocation, and prompt generation must log securely to the `EventBus` to ensure post-incident forensics.
