# PLAZA BOT

This is a bot which automatically applies to a list of Plaza Complexes every time a new one is available. It uses `python 3.11.9` with `hatchling` for building and `selenium` for `webdriver` interaction.

## Prerequisites

- Python 3.11.9 or higher
- Chrome browser (for Selenium WebDriver)
- A Plaza account

## Config Set-up

1. Create your own `config.yaml`
2. Fill in your Plaza account details (username, password)
3. Specify the city and province where you want the bot to search
4. Add a list of desired campuses (as street names)

Example config structure:

```yaml
login:
  url: "https://plaza.newnewnew.space/en/"
  username: "username"
  password: "password"

target:
  city: ["City", "Province"]
  complexes: ["Street Name"]

selenium:
  headless: True
  poll_interval: 60
```

## Installation & Usage

### From Source

1. Clone the repository:

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package:

   ```bash
   pip install .
   ```

4. Run the bot:

   ```bash
   python -m plaza_bot
   ```

### Using GitHub Release

1. Download the latest release from the GitHub repository
2. Extract the files
3. Create and edit your `config.yaml` file
4. Run the executable

## How to Contribute

Contributing to this project requires a slightly different setup to access development tools:

1. Fork and clone the repository

2. Create and activate a virtual environment

3. Install development dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

4. Available development commands:

   ```bash
   hatch run run      # Run the bot in development mode
   hatch run lint     # Check code style with linters
   hatch run format   # Auto-format code to match style guidelines
   hatch run test     # Run the test suite
   ```

5. Create a new branch for your feature or bug fix:

   ```bash
   git checkout -b feat/your-feature-name
   ```

6. Make your changes and commit them using [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) with descriptive messages
7. Push your branch and create a pull request

## Troubleshooting

- **WebDriver Issues**: Make sure you have Chrome installed and that the WebDriver version matches your Chrome version
- **Authentication Problems**: Verify your Plaza account credentials in the config file
