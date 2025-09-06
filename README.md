# Naukri Profile Updater

An automated tool to update your resume headline on Naukri.com, built with Python and Selenium.

## Overview

This project provides an automated solution for regularly updating your resume headline on Naukri.com. By keeping your profile active through regular updates, you can maintain better visibility with recruiters and the Naukri algorithm.

### Key Features

- **Automated Login**: Securely logs in to your Naukri account
- **Resume Headline Update**: Updates your resume headline with a customizable message
- **Headless Mode**: Runs in the background without opening a browser window (configurable)
- **Robust Error Handling**: Implements multiple retry mechanisms and comprehensive error handling
- **Detailed Logging**: Provides detailed logs for troubleshooting

## Requirements

- Python 3.7+
- Chrome browser
- ChromeDriver (automatically managed by webdriver-manager)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/moheedinamdar/naukri-profile-updater.git
   cd naukri-profile-updater
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your Naukri credentials:
   ```
   NAUKRI_EMAIL=your_email@example.com
   NAUKRI_PASSWORD=your_password
   ```

## Configuration

You can customize the application behavior by modifying the `variables.py` file:

- **Resume Headline**: Update the `RESUME_HEADLINE` variable with your desired headline text
- **Browser Visibility**: Set `RUN_HEADLESS = False` to see the browser automation in action
- **Wait Times**: Adjust timing parameters for different network conditions
- **Logging Level**: Change `LOG_LEVEL` to adjust verbosity (INFO, DEBUG, WARNING, ERROR)

## Usage

Run the script with:

```bash
python resume_headline_sync.py
```

The script will:
1. Launch Chrome (headless by default)
2. Log in to your Naukri account
3. Navigate to your profile
4. Update your resume headline
5. Verify the update was successful
6. Close the browser

## Scheduling Regular Updates

### Using GitHub Actions (Recommended):

This repository includes a GitHub Actions workflow that:
- Runs every weekday (Monday to Friday) at 8:00 AM IST
- Runs on every push to any branch
- Can be triggered manually on any branch

To set up:

1. Fork or push this repository to your GitHub account
2. Go to your repository's Settings → Environments → Create new environment (name it "dev")
3. Add the following environment secrets:
   - `NAUKRI_EMAIL`: Your Naukri.com email address
   - `NAUKRI_PASSWORD`: Your Naukri.com password
4. Configure environment protection rules and branch restrictions if needed

### Running the GitHub Action Manually on Any Branch

You can manually trigger the workflow on any branch:

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Select the "Naukri Profile Update" workflow from the left sidebar
4. Click the "Run workflow" dropdown button
5. Select the branch you want to run the workflow on
6. Optionally, provide a reason for the manual run
7. Click "Run workflow"

This is useful for testing your changes before merging to the main branch.

### On macOS/Linux (using cron):

1. Open your crontab:
   ```bash
   crontab -e
   ```

2. Add a schedule (e.g., every Monday at 9 AM):
   ```
   0 9 * * 1 cd /path/to/naukri-profile-updater && python resume_headline_sync.py >> cron.log 2>&1
   ```

### On Windows (using Task Scheduler):

1. Create a batch file (run_updater.bat):
   ```bat
   cd C:\path\to\naukri-profile-updater
   python resume_headline_sync.py
   ```

2. Open Task Scheduler and create a new task that runs this batch file on your preferred schedule

## Troubleshooting

If you encounter issues:

1. Check the console output for error messages
2. Set `RUN_HEADLESS = False` in `variables.py` to see the browser actions
3. Adjust wait times in `variables.py` if your internet connection is slow
4. Verify your credentials in the `.env` file

## Security Notes

- Never commit your `.env` file to version control
- Consider using a password manager to generate and store your Naukri password
- The script runs locally on your machine and doesn't transmit your credentials to any third-party services

## License

MIT

## Contributions

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## Disclaimer

This tool is for personal use only. Ensure you comply with Naukri.com's terms of service when using automated tools with their platform.