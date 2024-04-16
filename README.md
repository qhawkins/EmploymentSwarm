# Web Browsing Job Application Agent Swarm

This project serves as the foundation for a web browsing job application agent swarm. The system utilizes OpenAI's GPT-4 models to create intelligent agents capable of autonomously navigating websites, interacting with web elements, and performing tasks related to job applications.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Agents](#agents)
  - [Agent](#agent)
  - [BrowsingAgent](#browsingagent)
- [Tools](#tools)
- [Examples](#examples)
- [Future Development](#future-development)

## Overview

The Employment Swarm is designed to streamline and automate the process of applying for jobs online. By leveraging the power of GPT-4 models and web automation techniques, the system aims to create intelligent agents that can efficiently search for job opportunities, fill out application forms, and submit applications on behalf of the user.

The system is built upon an agent-based architecture, where each agent is responsible for a specific task or set of tasks related to the job application process. The agents work collaboratively as a swarm to accomplish the overall goal of applying for jobs.

## Installation

1. Clone the repository
2. Install the required dependencies:
   - openai
   - selenium
   - pyautogui
   - requests

## Usage

To run the web browsing job application agent swarm, execute the `main.py` script:

```bash
python main.py
```

## Agents

### Agent

The `Agent` class in `agent.py` serves as a base class for creating agents. It provides methods for initializing an agent, loading tools and prompts, creating threads and runs, and adding messages.

### BrowsingAgent

The `BrowsingAgent` class in `browsing_agent.py` extends the `Agent` class and provides functionality for web browsing and interaction. It uses Selenium for web automation and PyAutoGUI for cursor movement and interaction.

The `BrowsingAgent` class includes methods for:
- Loading a webpage
- Viewing a page and taking a screenshot
- Moving the cursor
- Getting the current URL
- Finding clickable elements and text elements
- Clicking elements
- Entering text into form fields
- Solving reCAPTCHA

## Tools

The `agent_tools.py` file contains a dictionary of tools that can be used by the agents. Currently, it includes a `prompt_user` function for prompting the user for input.

## Examples

The `main.py` script demonstrates how to use the `BrowsingAgent` to automate web browsing tasks. In the example, the agent is instructed to:
1. View a specific webpage
2. Click on various links
3. Fill out a contact form and submit it

The agent executes these tasks and retrieves the conversation messages at the end.

## Future Development

The web browsing job application agent swarm is a foundation for further development and expansion. Some potential areas for future development include:

- Implementing job search functionality to find relevant job listings
- Enhancing the agents' ability to understand and fill out complex job application forms
- Integrating natural language processing techniques to extract relevant information from job descriptions
- Developing a user interface for configuring and managing the agent swarm
- Incorporating machine learning algorithms to improve the agents' performance over time

Contributions and ideas for expanding the capabilities of the web browsing job application agent swarm are welcome.
