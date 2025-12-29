# WorkFlow Pro Automation Testing

hi! this is my testing project for WorkFlow Pro app. I made this for my automation testing practice and to show how i can test a real application.

## About the App

WorkFlow Pro is like a project management tool where companies can manage their projects. The main thing is that its multi-tenant which means different companies using the same app can't see each others data. pretty important security feature.

## What I Tested

I tried to cover the main features:

- Login stuff (with 2FA too)
- Making sure tenant isolation works
- Project creation and listing
- Some API testing
- Combined ui and api tests

## Tools Used

- Python (version 3.9)
- Playwright for browser testing
- pytest for running tests
- requests library for api calls
- github actions for ci/cd

## How to Setup

you need python installed on your machine. then:

```bash
# install dependencies
pip install -r requirements.txt

# install browsers for playwright
playwright install
```

## Project Structure

```
tests/
  api/           - api tests
  ui/            - ui tests  
  integration/   - combined tests
  data/          - test data file

conftest.py      - pytest setup
pytest.ini       - test config
requirements.txt - packages needed
```

## Running Tests

```bash
# run all tests
pytest

# run specific test file
pytest tests/ui/login_test.py

# run with html report
pytest --html=report.html
```

## Environment Setup

create a .env file with these variables:

```
BASE_URL=https://staging.workflowpro.com
API_BASE_URL=https://api-staging.workflowpro.com  
AUTH_TOKEN=your_token
TENANT_A_ID=tenant_uuid
TENANT_B_ID=another_tenant_uuid
```

## Test Data

test users and stuff are in tests/data/test_data.json file. you can update them based on your test environment.

This downloads Chromium, Firefox, and WebKit browsers that Playwright uses.

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Suites

```bash
# Only API tests
pytest tests/api/

# Only UI tests
pytest tests/ui/

## CI/CD 

i setup github actions so tests run automatically when you push code. check the .github/workflows folder for the config file.

to see test results:
- go to Actions tab on github
- click on the workflow run
- download the report if available

## Things I Learned

making this project i learned:
- how to handle 2FA in automated tests (used pyotp library)
- multi-tenant testing is important for security
- playwright is better than selenium for waiting 
- pytest fixtures are really useful
- ci/cd makes life easier

## Known Issues

some things still need work:
- need better error handling in some tests
- mobile testing not complete
- some selectors might break if ui changes

## Notes

- test data is in tests/data/test_data.json
- .env file has sensitive stuff so dont commit it
- reports folder gets created automatically when you run tests

thats it! hope this helps understand how i approached testing this app.

---

made by a fresher trying to learn automation testing :)
