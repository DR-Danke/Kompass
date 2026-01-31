# Prepare Application

Setup the application for the review or test.

## Variables

PORT: If `.ports.env` exists, read CLIENT_PORT from it, otherwise default to 5173
TEST_EMAIL: Read `TEST_ADMIN_EMAIL` from root `.env` file
TEST_PASSWORD: Read `TEST_ADMIN_PASSWORD` from root `.env` file

## Setup

1. Check if `.ports.env` exists:
   - If it exists, source it and use `CLIENT_PORT` for the PORT variable
   - If not, use default PORT: 5173

2. Reset the database:
   - Run `scripts/reset_db.sh`

3. Start the application:
   - IMPORTANT: Make sure the Server and Client are running on a background process using `nohup sh ./scripts/start.sh > /dev/null 2>&1 &`
   - The start.sh script will automatically use ports from `.ports.env` if it exists
   - Use `./scripts/stop_apps.sh` to stop the Server and Client

4. Verify the application is running:
   - The application should be accessible at http://localhost:PORT (where PORT is from `.ports.env` or default 5173)

5. Authenticate with test credentials:
   - IMPORTANT: Read `TEST_ADMIN_EMAIL` and `TEST_ADMIN_PASSWORD` from the root `.env` file
   - Navigate to http://localhost:PORT using Playwright
   - If redirected to login or if login button is visible, perform login:
     - Navigate to /login page
     - Fill the email field (data-testid="email-input") with `TEST_ADMIN_EMAIL` value
     - Fill the password field (data-testid="password-input") with `TEST_ADMIN_PASSWORD` value
     - Click the submit button (data-testid="login-submit")
     - Wait for redirect to dashboard or authenticated state
   - Verify login succeeded by checking for user info or logout button
   - IMPORTANT: Do NOT use hardcoded credentials like "admin@paqueteo.com" or "test@example.com"
   - IMPORTANT: Always use the actual values from `.env` file

Note: Read `scripts/` and `README.md` for more information on how to start, stop and reset the Server and Client.

