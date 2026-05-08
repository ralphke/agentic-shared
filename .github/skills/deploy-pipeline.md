# Skill: Deploy Pipeline Execution

**Persona:** DevOps/SRE Agent  
**Input:** Approved PR, infrastructure spec, IaC templates  
**Output:** Deployed application, deployment report, smoke test results

---

## When to Use This Skill

Use when a PR is approved and labelled `stage:deploy` by the Code Reviewer Agent.

---

## Execution Steps

1. **Validate pipeline config** — Check `.github/workflows/ci.yml` and orchestrator workflow
2. **Verify AI code provenance** — Confirm AI-assisted commits are tagged `[AI-assisted]`
   and that the Security Agent's SCA/license scan passed before proceeding.
3. **Build and scan image** — Build Docker image, run container vulnerability scan
4. **Deploy to dev** — Deploy to dev environment, run smoke tests
5. **Deploy to staging** — Deploy to staging, run full integration tests + perf baseline
6. **Production gate** — Manual approval for P0/P1; auto-advance for P2/P3
7. **Deploy to production** — Rolling deployment with health check validation
8. **Post-deploy monitoring** — Monitor error rate for 10 minutes
9. **Rollback if needed** — Auto-rollback if smoke tests fail or error rate spikes
10. **Report** — Post deployment summary on the PR
11. **Handoff** — Label issue `stage:operate`

---

## Deployment Commands Reference

```bash
# === Build ===
docker build \
  --target production \
  --build-arg VERSION=$(git describe --tags --always) \
  -t myapp:$(git rev-parse --short HEAD) .

# Container image scanning
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image myapp:$(git rev-parse --short HEAD)

# === Azure App Service ===
az webapp deploy \
  --resource-group $RG \
  --name $APP_NAME \
  --src-path ./dist \
  --slot staging

az webapp deployment slot swap \
  --resource-group $RG \
  --name $APP_NAME \
  --slot staging \
  --target-slot production

# === Kubernetes ===
kubectl set image deployment/$DEPLOYMENT \
  $CONTAINER=registry.io/myapp:$(git rev-parse --short HEAD) \
  -n $NAMESPACE

kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE
kubectl rollout undo deployment/$DEPLOYMENT -n $NAMESPACE  # rollback

# === Smoke Tests ===
./scripts/smoke-test.sh https://$ENV_URL
```

---

## Rollback Decision Matrix

| Condition                         | Action                    | Time Limit |
|-----------------------------------|---------------------------|------------|
| ≥ 3 smoke test failures           | Auto-rollback             | 5 min      |
| Error rate > 1% for > 5 min       | Auto-rollback             | 5 min      |
| p99 latency > 2x baseline         | Alert + manual decision   | 10 min     |
| Health check fails                | Auto-rollback immediately | Instant    |
| SEV-1 reported by user            | Manual rollback           | ASAP       |

---

## Deployment Report Template

```markdown
## Deployment Report — <change-slug>

**Deployed by:** DevOps/SRE Agent  
**Date:** YYYY-MM-DD HH:MM UTC  
**Environment:** production  
**Version:** <git-sha>  
**Result:** ✅ SUCCESS / ❌ ROLLED BACK

### Stage Results
| Stage   | Status | Duration | Notes          |
|---------|--------|----------|----------------|
| Build   | ✅     | 2m 15s   | Image scanned  |
| Dev     | ✅     | 1m 30s   | Smoke tests: 5/5|
| Staging | ✅     | 3m 45s   | Integration: 42/42|
| Prod    | ✅     | 2m 10s   | Smoke tests: 5/5|

### Post-Deploy Metrics (10-min window)
- Error rate: 0.02% (baseline: 0.01%) ✅
- p99 latency: 245ms (baseline: 230ms) ✅
- Availability: 100% ✅
```

---

## Quality Checks

- [ ] Image vulnerability scan completed (no CRITICAL CVEs)
- [ ] AI code provenance verified — AI-assisted commits tagged, SCA/license scan passed
- [ ] Smoke tests pass in dev and staging before production
- [ ] Rolling deployment used (no downtime)
- [ ] Health checks validated at each stage
- [ ] Rollback procedure tested (staging verified)
- [ ] Deployment report posted to PR
- [ ] Issue labelled `stage:operate`
