# Design Document

## Context

The current frontend build system has fundamental architectural flaws:
1. **Build location**: Happens on developer machines, not in Docker
2. **Dependency management**: Production-only installs skip build tools
3. **CSS configuration**: Uses CSS variable workarounds instead of proper Tailwind config
4. **Utility conflicts**: Custom CSS overrides Tailwind utilities

These issues prevent CI/CD automation and cause inconsistent styling across environments.

## Goals / Non-Goals

### Goals
- ? Deterministic builds in any environment
- ? Proper Tailwind configuration following best practices
- ? Clean separation between custom styles and utility classes
- ? Enable CI/CD automation

### Non-Goals
- ? Changing CSS class names in components (maintain compatibility)
- ? Redesigning UI or changing visual appearance
- ? Adding new CSS features or utilities
- ? Setting up CI/CD pipeline (enables it, doesn't implement it)

## Decisions

### Decision 1: Multi-Stage Docker Build

**What**: Use Docker multi-stage build with separate builder and runtime stages

**Why**:
- Builder stage can install all dependencies including devDependencies
- Runtime stage gets pre-built output with only production dependencies
- Ensures consistent build environment regardless of host machine
- Industry standard pattern for Node.js apps

**Alternatives considered**:
- ? Fix host builds - Still inconsistent, doesn't enable CI/CD
- ? Install all deps in production - Security risk, larger image
- ? Multi-stage build - Best practice, secure, consistent

### Decision 2: Tailwind Spacing Configuration

**What**: Define complete spacing scale in `tailwind.config.ts` theme

**Why**:
- Tailwind's recommended approach for customizing spacing
- Generates proper CSS without calc() or CSS variables
- Type-safe and autocomplete-friendly
- Consistent with Tailwind design system

**Alternatives considered**:
- ? Keep CSS variables - Fragile, error-prone, not idiomatic
- ? Manual utilities in CSS - Conflicts, maintenance burden
- ? Tailwind theme config - Standard, robust, maintainable

### Decision 3: Remove Custom Utilities

**What**: Remove `.gap-12` and other utility classes from `main.css`

**Why**:
- Prevents conflicts with Tailwind's utilities
- Makes behavior predictable (only one source of truth)
- Reduces maintenance burden
- Aligns with "use Tailwind, don't fight it" principle

**Alternatives considered**:
- ? Namespace custom utilities - Still conflicts, adds complexity
- ? Load order changes - Fragile, doesn't solve root issue
- ? Remove conflicting utilities - Clean, simple, maintainable

## Architecture

### Before (Broken)
```
Local Machine
  ?? npm install (dev + prod deps)
  ?? npm run build
  ?? .output/ created
       ?
Docker Container
  ?? npm ci --only=production (no build tools!)
  ?? COPY .output/ (pre-built)
  ?? Run server
```

**Problems**:
- Different node_modules = different CSS
- Can't build in CI/CD
- "Works on my machine" issues

### After (Fixed)
```
Docker Stage 1: Builder
  ?? npm ci (all deps)
  ?? COPY source
  ?? npm run build
  ?? .output/ created
       ?
Docker Stage 2: Runtime
  ?? npm ci --only=production
  ?? COPY .output/ from builder
  ?? Run server
```

**Benefits**:
- Same CSS every time
- Works in CI/CD
- Secure (no dev deps in runtime)

## Risks / Trade-offs

### Risk 1: Build Time Increase
**Mitigation**: Multi-stage build is well-optimized, increase should be minimal (<2 min)

### Risk 2: Breaking Changes in Styling
**Mitigation**: Thorough visual testing before deployment, rollback plan ready

### Risk 3: Developer Confusion
**Mitigation**: Clear documentation, quick reference guide provided

### Risk 4: Docker Image Size
**Mitigation**: Multi-stage keeps runtime image small (no build tools)

## Migration Plan

### Pre-Deployment
1. Backup current Docker image: `docker tag anwalts_frontend:latest anwalts_frontend:backup`
2. Test new Dockerfile locally
3. Visual comparison of dashboard and settings pages
4. Browser DevTools verification of CSS utilities

### Deployment
1. Build new image: `docker-compose build --no-cache frontend`
2. Stop old container: `docker-compose down frontend`
3. Start new container: `docker-compose up -d frontend`
4. Restart nginx: `docker restart anwalts_nginx`
5. Wait 30 seconds for health check
6. Verify dashboard loads correctly

### Rollback
If issues detected within 24 hours:
```bash
docker stop anwalts_frontend
docker rm anwalts_frontend
docker tag anwalts_frontend:backup anwalts_frontend:latest
docker-compose up -d frontend
docker restart anwalts_nginx
```

Or via git:
```bash
cd /root
git revert <commit-hash>
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## Open Questions

- ~~Should we add PostCSS minification?~~ ? Yes, added to proposal (Stage 2)
- ~~Should we set up CI/CD now?~~ ? No, this change enables it but doesn't implement it
- ~~Should we validate CSS output?~~ ? Yes, add validation script (Stage 2, optional)

## Technical Details

### Dockerfile Changes
- Add `FROM node:20-alpine AS builder` for build stage
- Run `npm ci` (not --only=production) in builder
- Run `npm run build` in builder
- Use `COPY --from=builder` to get .output in runtime stage
- Keep production npm ci in runtime stage

### Tailwind Config Changes
- Add `spacing` object to `theme.extend`
- Define values: 0, 0.5, 1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24, etc.
- Use rem units (0.25rem, 0.5rem, 1rem, etc.)
- Follow Tailwind's default scale

### CSS File Changes
- `tailwind.css`: Remove `:root { --spacing: 0.25rem; }`
- `main.css`: Remove `.gap-12 { gap: 12px; }`
- Keep custom CSS variables for project-specific values
- Keep custom component styles (`.card--padded`, etc.)

## Validation

### Pre-Deployment Checklist
- [ ] Dockerfile has `AS builder` stage
- [ ] `npm ci` (not --only=production) in builder
- [ ] `COPY --from=builder` in runtime
- [ ] Tailwind config has `spacing` object
- [ ] `tailwind.css` has no `--spacing` variable
- [ ] `main.css` has no `.gap-12` utility

### Post-Deployment Checklist
- [ ] Docker build succeeds
- [ ] Container starts and passes health check
- [ ] Dashboard cards have proper spacing
- [ ] Settings page forms fully styled
- [ ] Browser console has no CSS errors
- [ ] Page load time acceptable
