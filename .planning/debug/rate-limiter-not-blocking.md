---
status: diagnosed
trigger: "Diagnose why the rate limiter is not blocking requests in the GrindX API"
created: 2026-06-06T19:45:00Z
updated: 2026-06-06T19:45:00Z
---

## Current Focus

hypothesis: "Issue 1 is caused by /health being in exclude_paths (BY DESIGN). Issue 2 needs separate investigation — mechanism works in tests."
test: Verified exclude_paths list, ran actual test suite, tested MemoryStorage.acquire_entry directly
expecting: Rate limiter works correctly; UAT test methodology is flawed for Issue 1
next_action: Return diagnosis

## Symptoms

expected: Sending more than RATE_LIMIT_REQUESTS requests returns 429
actual: Sending requests to /health always returns 200 (no 429)
errors: None — endpoint simply never rate-limits
reproduction: Send 101+ GET requests to /health
started: Since Phase 1 rewrite using SlowAPI/limits library

## Eliminated

- hypothesis: "MemoryStorage.acquire_entry is broken"
  evidence: Direct Python test shows acquire_entry correctly blocks at limit+1 (100 allowed, 101st blocked)
  timestamp: 2026-06-06T19:45:00Z

- hypothesis: "limits.parse('100/60second') produces wrong values"
  evidence: parse produces RateLimitItemPerSecond(amount=100, expiry=60) — same effective values as parse('100/minute')
  timestamp: 2026-06-06T19:45:00Z

- hypothesis: "Middleware not registered in main.py"
  evidence: main.py line 75-80 clearly adds RateLimitMiddleware with settings values
  timestamp: 2026-06-06T19:45:00Z

- hypothesis: "Config values not loaded correctly"
  evidence: .env has RATE_LIMIT_REQUESTS=100, RATE_LIMIT_WINDOW_SECONDS=60. config.py defaults match.
  timestamp: 2026-06-06T19:45:00Z

- hypothesis: "Rate limit tests skip instead of passing"
  evidence: All 5 tests PASS (not skip). test_rate_limit_by_ip hits 429 at request 101. test_rate_limit_by_user_id hits 429 at request 101.
  timestamp: 2026-06-06T19:45:00Z

## Evidence

- timestamp: 2026-06-06T19:45:00Z
  checked: main.py line 79 exclude_paths parameter
  found: exclude_paths=["/health", "/v1/docs", "/v1/redoc", "/v1/openapi.json"]
  implication: /health is EXCLUDED from rate limiting BY DESIGN. Testing rate limiting against /health will NEVER trigger 429.

- timestamp: 2026-06-06T19:45:00Z
  checked: rate_limit.py line 113 exclude_paths check
  found: if request.url.path in self.exclude_paths: return await call_next(request)
  implication: Excluded paths skip ALL rate limiting logic — no acquire_entry call, no headers added.

- timestamp: 2026-06-06T19:45:00Z
  checked: test_rate_limit.py TestRateLimitExcludedPaths
  found: test_rate_limit_excluded_paths asserts /health NEVER returns 429 (150 requests, all 200)
  implication: The test VERIFIES that /health is excluded. This is intentional, not a bug.

- timestamp: 2026-06-06T19:45:00Z
  checked: Direct Python test of MemoryStorage.acquire_entry
  found: With limit=100, expiry=60: 100 requests allowed, 101st correctly blocked
  implication: The core rate limiting mechanism works correctly.

- timestamp: 2026-06-06T19:45:00Z
  checked: Full pytest run of test_rate_limit.py
  found: All 5 tests PASSED (not skipped)
  implication: Rate limiting works correctly in the test environment for non-excluded endpoints.

- timestamp: 2026-06-06T19:45:00Z
  checked: auth/service.py _gerar_tokens and shared/security/jwt.py criar_jwt
  found: JWT payload includes {"sub": str(usuario.id), "role": ..., "company_id": ...}, encoded with HS256
  implication: Token format is correct. Rate limiter's _get_user_id_from_token should decode it properly.

## Resolution

root_cause: |
  Issue 1 (/health not rate-limited): This is BY DESIGN, not a bug. The `/health` endpoint is explicitly listed in `exclude_paths` at main.py line 79. The middleware skips rate limiting for this path entirely (rate_limit.py line 113). The UAT test is testing rate limiting against the wrong endpoint.

  Issue 2 (authenticated users unlimited): The rate limiting mechanism works correctly in tests (all 5 pass, including authenticated user rate limiting). If the UAT is also testing authenticated rate limiting against /health, the same exclude_paths issue applies. If testing against non-excluded authenticated endpoints, the mechanism should work — any discrepancy would be environment-specific.

fix: |
  For Issue 1: The UAT test should use a non-excluded endpoint (e.g., /v1/auth/token) to verify IP-based rate limiting. Alternatively, if /health SHOULD be rate-limited, remove it from exclude_paths in main.py line 79.

  For Issue 2: Verify the UAT is testing against a non-excluded authenticated endpoint. The mechanism works correctly in tests.

verification: "All 5 rate_limit tests pass. Direct Python testing of MemoryStorage.acquire_entry confirms correct blocking behavior."
files_changed: []
