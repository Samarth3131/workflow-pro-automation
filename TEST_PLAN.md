# Test Plan

## What im testing

this document has my testing strategy for WorkFlow Pro application.

## Main Areas to Test

### 1. Login & Authentication
- login with correct username/password
- login with wrong credentials
- 2FA if enabled
- logout functionality

### 2. Multi-tenant Stuff
- user from company A cant see company B's data
- switching between tenants if user has access to multiple
- data isolation is working properly

### 3. Projects
- create new project
- see list of projects
- view project details
- delete project
- check permissions (who can do what)

### 4. API Testing
- GET /api/projects - get all projects
- POST /api/projects - create project
- DELETE /api/projects/{id} - delete project
- verify tenant isolation in api calls

### 5. End to End Flows
- create project in ui and verify it exists in api
- create via api and check it shows in ui
- delete project and make sure its gone everywhere

## Test Types

### Smoke Tests
basic tests that run first to check if app is working:
- can login
- can see dashboard
- api is responding

### Functional Tests
detailed feature testing:
- all project operations
- user management
- tenant switching

### Integration Tests
testing how different parts work together:
- ui + api combined
- multiple user actions in sequence

## Tools

- pytest for test framework
- playwright for browser automation
- requests for api calls
- github actions for running tests automatically

## Test Data

using test_data.json file for:
- test users for different tenants
- sample project data
- api endpoints

## Out of Scope

not testing these for now:
- performance/load testing
- security penetration testing
- mobile app (if there is one)
- payment processing
- email notifications

## Test Environment

- staging environment: staging.workflowpro.com
- test accounts setup in test data file
- using chrome browser mainly
- python 3.9+

## Success Criteria

tests pass if:
- all login scenarios work
- tenant isolation is strict (no data leakage)
- projects can be created/deleted properly
- api and ui are in sync
- no critical bugs found

- Performance/Load testing   - Cart persistence across pages

- Security penetration testing (separate effort)   - Multiple items management

- Mobile app testing

- Email notification testing4. **Checkout Process**

- Third-party integrations (Slack, Jira, etc.)   - Checkout information form

- Database testing   - Form validation

- Infrastructure testing   - Order review

   - Order completion

## 4. Test Approach   - Order confirmation



### Test Levels#### Medium Priority

5. **Navigation**

1. **API Tests** - Fast, stable, test business logic   - Menu functionality

2. **UI Tests** - Cover user-critical flows   - Back navigation

3. **Integration Tests** - End-to-end scenarios   - Continue shopping

   - Page transitions

### Test Types

6. **UI/UX Elements**

- **Smoke Tests** - Critical path verification (login → create project → view project)   - Responsive design

- **Regression Tests** - Full test suite before releases   - Button states

- **Functional Tests** - Feature-by-feature validation   - Error messages

   - Loading states

### Automation Strategy

#### Low Priority

- **70% API tests** - Faster, more reliable7. **Social Media Links**

- **20% UI tests** - User-critical journeys only8. **Footer Information**

- **10% Integration** - End-to-end flows

### 2.2 Features NOT to be Tested

## 5. Test Environment- Payment gateway integration (out of scope for demo site)

- Email notifications

### Environments- Third-party integrations

- Backend API (focus on UI automation)

- **Staging:** `https://staging.workflowpro.com` (primary test env)- Performance testing (separate effort)

- **QA:** `https://qa.workflowpro.com` (for feature testing)- Security testing (separate effort)



### Test Data---



**Tenant A (Company A):**## 3. Test Strategy

- User: user1@companyA.com

- Admin: admin@companyA.com### 3.1 Testing Approach

- **Automation Framework**: Selenium WebDriver with Python

**Tenant B (Company B):**- **Test Framework**: pytest

- User: user2@companyB.com- **Design Pattern**: Page Object Model (POM)

- Admin: admin@companyB.com- **Reporting**: pytest-html, Allure Reports

- **CI/CD**: GitHub Actions

Test accounts have 2FA disabled or use fixed TOTP secrets.

### 3.2 Test Levels

## 6. Test Scenarios

#### 3.2.1 Smoke Tests

### 6.1 Authentication TestsCritical path testing to ensure basic functionality works.

- Login with valid credentials

| ID | Test Case | Priority | Type |- Add one product to cart

|----|-----------|----------|------|- Complete checkout process

| AUTH_001 | Login with valid credentials | High | Smoke |- Logout

| AUTH_002 | Login with invalid credentials | High | Functional |

| AUTH_003 | 2FA code validation | Medium | Functional |**Execution Frequency**: Before each test cycle, after each deployment

| AUTH_004 | Session timeout handling | Medium | Functional |

| AUTH_005 | Logout clears session | High | Smoke |#### 3.2.2 Functional Tests

Detailed testing of all features and user workflows.

### 6.2 Multi-Tenant Tests- All login scenarios

- Product catalog operations

| ID | Test Case | Priority | Type |- Cart management

|----|-----------|----------|------|- Complete checkout flows

| MT_001 | User A sees only Tenant A projects | Critical | Smoke |- Navigation tests

| MT_002 | User B cannot access Tenant A projects | Critical | Smoke |

| MT_003 | API returns 403 for cross-tenant access | Critical | API |**Execution Frequency**: Daily, on-demand

| MT_004 | User switches between assigned tenants | High | Functional |

#### 3.2.3 Regression Tests

### 6.3 Project Management TestsFull test suite to ensure existing functionality remains intact.

- All test cases

| ID | Test Case | Priority | Type |- Cross-browser testing

|----|-----------|----------|------|- Data-driven tests

| PROJ_001 | Create project via UI | High | Smoke |

| PROJ_002 | Create project via API | High | API |**Execution Frequency**: Weekly, before releases

| PROJ_003 | List all projects for tenant | High | API |

| PROJ_004 | View project details | Medium | Functional |### 3.3 Test Types

| PROJ_005 | Delete project (Admin only) | High | Functional |

| PROJ_006 | Member cannot delete project | High | Functional || Test Type | Description | Coverage |

|-----------|-------------|----------|

### 6.4 Integration Tests| UI Tests | Frontend user interface testing | 80% |

| Integration | Component interaction testing | 15% |

| ID | Test Case | Priority | Type || Smoke | Critical path validation | 5% |

|----|-----------|----------|------|

| INT_001 | Create via UI, verify via API | High | Integration |### 3.4 Automation Coverage Goal

| INT_002 | Create via API, verify in UI | High | Integration |- **Target**: 85% automation coverage

| INT_003 | Delete via API, verify removed in UI | Medium | Integration |- **Priority**: High and Medium priority features

- **Timeline**: 2 weeks for initial framework, 3 weeks for full coverage

## 7. Entry & Exit Criteria

---

### Entry Criteria

- Test environment is stable and accessible## 4. Test Environment

- Test data is prepared

- Application build is deployed### 4.1 Software Requirements

- Test automation framework is set up- **Python**: 3.9+

- **Selenium WebDriver**: 4.x

### Exit Criteria- **pytest**: 7.x

- 100% of critical tests pass- **Browsers**: Chrome (latest), Firefox (latest), Edge (latest)

- 95%+ of high-priority tests pass- **OS**: Windows 10/11, macOS, Linux

- No critical defects open

- Test report generated and reviewed### 4.2 Test Environment URLs

- **Production**: https://www.saucedemo.com

## 8. Defect Management- **Staging**: https://staging.saucedemo.com (if available)



**Severity Levels:**### 4.3 Test Data

- **Critical** - System crash, security breach, data loss- Test user accounts (provided by application)

- **High** - Major feature broken, blocking issue- Product catalog data

- **Medium** - Feature partially working, workaround exists- Valid/Invalid test inputs

- **Low** - Minor UI issues, cosmetic problems- Boundary value test data



## 9. Risks & Mitigation---



| Risk | Impact | Mitigation |## 5. Test Execution Strategy

|------|--------|------------|

| 2FA blocks automation | High | Use test accounts with 2FA disabled or TOTP library |### 5.1 Test Execution Schedule

| Test data conflicts | Medium | Use unique data per test run (timestamps) || Phase | Duration | Activities |

| Environment downtime | High | Have fallback QA environment ||-------|----------|------------|

| Setup | Week 1 | Framework setup, POM implementation |

## 10. Tools & Technologies| Development | Week 2-3 | Test script development |

| Execution | Week 4 | Full test suite execution |

- **Playwright** - UI automation (Python sync API)| Reporting | Week 4 | Results analysis and reporting |

- **Requests** - API testing

- **pytest** - Test framework### 5.2 Entry Criteria

- **pytest-html** - HTML reporting- Test environment is available and stable

- **GitHub Actions** - CI/CD- Test data is prepared

- All test scripts are reviewed and approved

## 11. Test Execution Schedule- Required tools and frameworks are installed



- **Daily:** Smoke tests on every deployment### 5.3 Exit Criteria

- **Nightly:** Full regression suite- All planned test cases executed

- **On-demand:** Feature-specific tests during development- 95%+ test pass rate for smoke tests

- 85%+ test pass rate for regression tests

## 12. Deliverables- All critical and high severity defects resolved

- Test reports generated and reviewed

- Test automation framework (this repo)

- Test execution reports (HTML)---

- Defect reports (logged in Jira/GitHub Issues)

- Test metrics dashboard## 6. Test Deliverables



## 13. Success Metrics### 6.1 Before Testing

- ✅ Test Plan (this document)

- **Test Coverage:** 80%+ of critical features- ✅ Test Cases Documentation

- **Automation Rate:** 85%+ automated- ✅ Test Automation Framework

- **Pass Rate:** 95%+ in stable environment- ✅ Test Data Sets

- **Execution Time:** < 30 minutes for full suite

### 6.2 During Testing

---- Test Execution Logs

- Defect Reports

**Document Owner:** QA Team  - Progress Reports

**Last Updated:** December 2025  

**Version:** 1.0### 6.3 After Testing

- Test Summary Report
- Test Metrics Dashboard
- Lessons Learned Document
- Updated Test Cases

---

## 7. Test Cases Overview

### 7.1 Test Case Categories

| Category | Test Cases | Priority | Automation |
|----------|------------|----------|------------|
| Authentication | 8 | High | Yes |
| Product Catalog | 12 | High | Yes |
| Shopping Cart | 10 | High | Yes |
| Checkout | 15 | High | Yes |
| Navigation | 8 | Medium | Yes |
| UI/UX | 10 | Medium | Partial |
| **Total** | **63** | - | **95%** |

---

## 8. Risk Assessment

### 8.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Browser compatibility issues | High | Medium | Test on multiple browsers, use WebDriver Manager |
| Element locator instability | High | Medium | Use robust locator strategies, implement waits |
| Test data dependencies | Medium | Low | Create independent test data sets |
| Environment unavailability | High | Low | Use local test environment fallback |

### 8.2 Project Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Timeline delays | Medium | Low | Prioritize critical tests first |
| Resource unavailability | High | Low | Cross-train team members |
| Scope creep | Medium | Medium | Strict change control process |

---

## 9. Resource Requirements

### 9.1 Human Resources
- **QA Automation Engineer**: 1 (Full-time)
- **QA Lead**: 1 (Part-time for reviews)

### 9.2 Tools & Infrastructure
- Python development environment
- Selenium WebDriver
- Git & GitHub
- CI/CD pipeline (GitHub Actions)
- Test reporting tools

---

## 10. Test Metrics

### 10.1 Key Performance Indicators

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Automation Coverage | 85% | (Automated Tests / Total Tests) × 100 |
| Test Pass Rate | 90% | (Passed Tests / Total Tests) × 100 |
| Defect Detection Rate | >80% | Defects found / Total Defects |
| Test Execution Time | <30 min | Total suite execution time |
| Average Test Stability | 95% | Consistent pass rate over 10 runs |

### 10.2 Reporting Frequency
- **Daily**: Test execution results
- **Weekly**: Test metrics dashboard
- **Milestone**: Comprehensive test report

---

## 11. Defect Management

### 11.1 Defect Severity Levels

| Level | Description | Example | Response Time |
|-------|-------------|---------|---------------|
| Critical | System crash, data loss | Login not working for all users | 2 hours |
| High | Major feature broken | Checkout process fails | 4 hours |
| Medium | Feature partially works | Sorting not working correctly | 1 day |
| Low | Minor UI issues | Text alignment off | 3 days |

### 11.2 Defect Lifecycle
1. New → Open → In Progress → Fixed → Ready for Testing → Closed
2. All defects logged with screenshots, steps to reproduce, and environment details

---

## 12. Assumptions and Dependencies

### 12.1 Assumptions
- Test environment is available 24/7
- Application functionality remains stable during test development
- Test user accounts are always accessible
- No major architectural changes during testing phase

### 12.2 Dependencies
- Application deployment schedule
- Test environment setup completion
- Tool licenses and access
- Test data availability

---

## 13. Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| QA Lead | [To be filled] | | |
| Project Manager | [To be filled] | | |
| Development Lead | [To be filled] | | |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-30 | QA Team | Initial test plan created |

---

**End of Test Plan**
