# Home Rush

This is a bot which applies to differnt housing agency complexes. It uses `python 3.11.9` with `hatchling` for building and `selenium` for `webdriver` interaction. The bot can create multiple instances that run in parallel, allowing for efficient monitoring and application across different platforms.

> Right now, it only works with Plaza Resident Services, but I am extending it to work with Holland2Stay and other agencies.

## Prerequisites

- Python 3.11.9 or higher
- Chrome browser (for Selenium WebDriver)
- A Plaza account

## Config Set-up

1. Create your own `config.yaml`
2. Specify the agency you want (only `plaza` works for now).
3. Fill in your account details (username, password)
4. Specify the city and province where you want the bot to search
5. Add a list of desired campuses (as street names)

### Example config structure:

```yaml
plaza:
  login:
    url: "https://plaza.newnewnew.space/en/"
    username: "your_username"
    password: "your_password"

  target:
    city: ["City", "Province"]
    complexes: ["Street Name"]

  poll_interval: 60

selenium:
  headless: True / False
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
  python -m home_rush
  ```

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
- **Authentication Problems**: Verify your account credentials in the config file
