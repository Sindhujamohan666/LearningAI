# Company QA Standards & Policies

## Testing Standards
- All critical paths must have automated test coverage
- Code coverage minimum: 80% for unit tests, 60% for integration tests
- Every PR must pass smoke tests before merge
- Defects found in production must have a corresponding regression test added

## Severity Classification
- **Critical**: System down, data loss, security breach → Fix within 4 hours
- **High**: Core feature broken, no workaround → Fix within 24 hours
- **Medium**: Feature partially broken, workaround exists → Fix within 1 sprint
- **Low**: Cosmetic, minor inconvenience → Backlog

## Test Case Naming Convention
`[Module]_[Feature]_[Scenario]_[ExpectedResult]`

## Browser Support Matrix
| Browser | Versions | Priority |
|---------|----------|----------|
| Chrome | Latest, Latest-1 | P0 |
| Firefox | Latest | P0 |
| Safari | Latest | P0 |
| Edge | Latest | P1 |
| Mobile Safari | Latest | P0 |
| Mobile Chrome | Latest | P0 |

## Release Criteria
- All P0/P1 tests passing
- No open Critical/High bugs
- Performance benchmarks within 10% of baseline
- Security scan clean
- Accessibility score >= 90
