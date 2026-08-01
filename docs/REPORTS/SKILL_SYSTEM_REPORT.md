# Skill System Report
## Overview
Skills are validated via `SkillValidationSchema` in Pydantic and exposed to agents.
## OMNI Upgrade Path
- **Discovery:** Implement automatic semantic discovery of skills using the Vector Store so agents can dynamically request missing skills at runtime.
- **Versioning:** Enforce strict semantic versioning to ensure backward compatibility as skills evolve.
