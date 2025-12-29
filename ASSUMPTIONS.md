# Assumptions

here are things i assumed while making these tests. if any of this is wrong the tests might break.

## About the App

### Login
- login page is at /login
- username and password fields exist
- 2FA might be enabled (using pyotp library to handle it)
- after login redirects to /projects or /dashboard

### Multi-tenant Setup
- each company (tenant) has separate data
- users cant see other company's data
- tenant id is sent in api headers like X-Tenant-ID
- app doesnt let you access other tenant's stuff (returns 403 error)

### Projects
- projects have id, name, description
- anyone can create projects
- only certain roles can delete
- projects are listed on /projects page

### API Endpoints
assuming these apis exist:
- GET /api/projects - gets all projects
- POST /api/projects - creates new project  
- DELETE /api/projects/{id} - deletes project

apis need authentication token in header.

### UI Selectors
assuming common html elements:
- login form has email and password inputs
- buttons have text like "Login", "Create Project"
- might need to update selectors if ui changes

## Test Environment

- using staging environment (not production!)
- test accounts already setup
- environment is stable most of the time
- no data gets deleted randomly

## Test Data

- test users are in test_data.json
- each tenant has 2-3 test users
- project names are unique with timestamps to avoid conflicts

## Limitations

- not testing on real mobile devices (just browser emulation)
- assuming english language only
- not testing all edge cases (focusing on main flows)
- tests might take longer if network is slow

if anything breaks check these assumptions first!

- **Pre-created Accounts:** Test users already exist (or we can create them)
- **Pre-created Tenants:** At least 2 tenants exist for cross-tenant testing
- **Data Cleanup:** Either:
  - Tests clean up after themselves (delete created projects), OR
  - Environment is reset nightly
  
  *(I chose: tests use unique names with timestamps, minimal cleanup needed)*

### 3. Browser Support

- **Chromium:** Primary browser for automation
- **Firefox/WebKit:** Optional, for cross-browser testing
- **Headless Mode:** Works without display (for CI)

### 4. Network & Performance

- **Latency:** < 2 seconds for most API calls
- **Page Load:** < 5 seconds for UI pages
- **No CAPTCHA:** Test accounts bypass CAPTCHA

## CI/CD Assumptions

### 1. GitHub Actions

- **Free Minutes:** Sufficient for our test runs (<2000 minutes/month)
- **Secrets:** Can store credentials in GitHub Secrets
- **Artifacts:** Can upload HTML reports (retention: 90 days)

### 2. BrowserStack (Optional)

- **Account Access:** If using BrowserStack, credentials are provided
- **Parallel Tests:** Can run multiple tests simultaneously
- **Browser Matrix:** Supports Playwright

## Security Assumptions

### 1. Credentials Management

- **Not in Code:** Real passwords NOT committed to repo
- **Environment Variables:** Credentials loaded from `.env` or GitHub Secrets
- **Test Accounts:** Using dedicated test accounts, not real user data

### 2. Tenant Data Privacy

- **No PII:** Test data doesn't contain real personal information
- **Synthetic Data:** All test projects, users, etc. are fake

## Known Limitations

### 1. Email Testing

- **Assumption:** Email notifications are NOT tested
- **Reason:** Requires email service integration or mail traps
- **Alternative:** Can test via API if email service has API

### 2. File Uploads

- **Assumption:** Project attachments/files NOT tested yet
- **Reason:** File handling needs separate test data setup
- **Future:** Can add if needed

### 3. Webhooks & Integrations

- **Assumption:** Third-party integrations (Slack, Jira) NOT tested
- **Reason:** Out of scope for initial automation

### 4. Mobile/Responsive

- **Assumption:** Testing desktop web only
- **Reason:** Mobile app is separate, responsive web TBD

## What Happens If Assumptions Are Wrong?

If any assumptions are incorrect:

1. **Update this doc** with correct info
2. **Adjust test code** accordingly
3. **Re-run tests** to verify

Common adjustments needed:
- Update API endpoints in `test_data.json`
- Update UI selectors in test files
- Adjust authentication method
- Change tenant identification approach

## Questions to Clarify

If you're the project stakeholder, please confirm:

1. ✅ What's the actual authentication flow? (Username/email + password + 2FA?)
2. ✅ How is tenant context passed? (Header, subdomain, token claim?)
3. ✅ Can test accounts have 2FA disabled?
4. ✅ What are the exact API endpoints?
5. ✅ What permissions do test users have?
6. ✅ Can we create/delete test data freely?

---

**Last Updated:** December 2025  
**Review:** Update assumptions as we learn more about the actual system
