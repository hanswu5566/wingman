# Wingman

![Wingman Logo](wingman.png)

Wingman is a LLM-powered AI assistant designed to help users utilize natural language to enhance efficiency in comprehending information and conversations over company Slack workspaces and to manipulate ClickUp for better task management efficiency.

## Features

- **Natural Language Processing**: Use natural language to interact with Slack and ClickUp.
- **Boost Efficiency**: Automate and streamline communication and task management.
- **Integration with Slack**: Enhance conversations and information retrieval within Slack.
- **Integration with ClickUp**: Improve task management and project tracking within ClickUp.

## Getting Started

### Prerequisites

- Python 3.12.0
- Slack Workspace
- ClickUp account

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/hanswu5566/wingman.git
    cd wingman
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up environment variables:
    - Create a `.env` file in the root directory and add your configuration details:
    ```env
    SLACK_API_TOKEN=your_slack_api_token
    CLICKUP_API_TOKEN=your_clickup_api_token
    ```

### Usage

1. Run the application:
    ```sh
    python app.py
    ```

2. Interact with Wingman via Slack:
    - Send commands and queries in natural language.
 
