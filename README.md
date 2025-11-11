# PagerDuty's official MCP Server

<!-- mcp-name: io.github.PagerDuty/pagerduty-mcp -->

PagerDuty's local MCP (Model Context Protocol) server which provides tools to interact with your PagerDuty account, allowing you to manage incidents, services, schedules, event orchestrations, and more directly from your MCP-enabled client.

## Prerequisites

*   [asdf-vm](https://asdf-vm.com/) installed.
*   [uv](https://github.com/astral-sh/uv) installed globally. 
*   A PagerDuty **User API Token**.
    To obtain a PagerDuty User API Token, follow these steps:

    1. **Navigate to User Settings.** Click on your user profile icon, then select **My Profile** and then **User Settings**.
        > For **Freemium** accounts, the permissions for generating User API tokens are limited to the user role as defined [here](https://support.pagerduty.com/main/docs/user-roles).
    2. In your user settings, locate the **API Access** section.
    3. Click the **Create API User Token** button and follow the prompts to generate a new token.
    4. **Copy the generated token and store it securely**. You will need this token to configure the MCP server.

    > Use of the PagerDuty User API Token is subject to the [PagerDuty Developer Agreement](https://developer.pagerduty.com/docs/pagerduty-developer-agreement).

## Using with MCP Clients

### Cursor Integration

You can configure this MCP server directly within Cursor's `settings.json` file, by following these steps:

1.  Open Cursor settings (Cursor Settings > Tools > Add MCP, or `Cmd+,` on Mac, or `Ctrl+,` on Windows/Linux).
2.  Add the following configuration:

    ```json
    {
      "mcpServers": {
        "pagerduty-mcp": {
          "type": "stdio",
          "command": "uvx",
          "args": [
            "pagerduty-mcp",
            "--enable-write-tools"
            // This flag enables write operations on the MCP Server enabling you to creating incidents, schedule overrides and much more
          ],
          "env": {
            "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}"
          }
        }
      }
    }
    ```

### VS Code Integration

You can configure this MCP server directly within Visual Studio Code's `settings.json` file, allowing VS Code to manage the server lifecycle.

1.  Open VS Code settings (File > Preferences > Settings, or `Cmd+,` on Mac, or `Ctrl+,` on Windows/Linux).
2.  Search for "mcp" and ensure "Mcp: Enabled" is checked under Features > Chat.
3.  Click "Edit in settings.json" under "Mcp > Discovery: Servers".
4.  Add the following configuration:

    ```json
    {
        "mcp": {
            "inputs": [
                {
                    "type": "promptString",
                    "id": "pagerduty-api-key",
                    "description": "PagerDuty API Key",
                    "password": true
                }
            ],
            "servers": {
                "pagerduty-mcp": { 
                    "type": "stdio",
                    "command": "uvx",
                    "args": [
                        "pagerduty-mcp",
                        "--enable-write-tools"
                        // This flag enables write operations on the MCP Server enabling you to creating incidents, schedule overrides and much more
                    ],
                    "env": {
                        "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}",
                        "PAGERDUTY_API_HOST": "https://api.pagerduty.com"
                        // If your PagerDuty account is located in EU update your API host to https://api.eu.pagerduty.com
                    }
                }
            }
        }
    }
    ```

#### Trying it in VS Code Chat (Agent)

1.  Ensure MCP is enabled in VS Code settings (Features > Chat > "Mcp: Enabled").
2.  Configure the server as described above.
3.  Open the Chat view in VS Code (`View` > `Chat`).
4.  Make sure `Agent` mode is selected. In the Chat view, you can enable or disable specific tools by clicking the 🛠️ icon.
5.  Enter a command such as `Show me the latest incident` or `List my event orchestrations` to interact with your PagerDuty account through the MCP server.
6.  You can start, stop, and manage your MCP servers using the command palette (`Cmd+Shift+P`/`Ctrl+Shift+P`) and searching for `MCP: List Servers`. Ensure the server is running before sending commands. You can also try to restart the server if you encounter any issues.

### Claude Desktop Integration

You can configure this MCP server to work with Claude Desktop by adding it to Claude's configuration file.

1.  **Locate your Claude Desktop configuration file:**
    -   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
    -   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

2.  **Create or edit the configuration file** and add the following configuration:

    ```json
    {
      "mcpServers": {
        "pagerduty-mcp": {
          "command": "uvx",
          "args": [
            "pagerduty-mcp",
            "--enable-write-tools"
          ],
          "env": {
            "PAGERDUTY_USER_API_KEY": "your-pagerduty-api-key-here",
            "PAGERDUTY_API_HOST": "https://api.pagerduty.com"
          }
        }
      }
    }
    ```

3.  **Replace the placeholder values:**
    -   Replace `/path/to/your/mcp-server-directory` with the full path to the directory where you cloned the MCP server (e.g., `/Users/yourname/code/pagerduty-mcp`)
    -   Replace `your-pagerduty-api-key-here` with your actual PagerDuty User API Token
    -   If your PagerDuty account is located in the EU, update the API host to `https://api.eu.pagerduty.com`

4.  **Restart Claude Desktop** completely for the changes to take effect.

5.  **Test the integration** by starting a conversation with Claude and asking something like "Show me my latest PagerDuty incidents" or "List my event orchestrations" to verify the MCP server is working.

    > **Security Note:** Unlike VS Code's secure input prompts, Claude Desktop requires you to store your API key directly in the configuration file. Ensure this file has appropriate permissions (readable only by your user account) and consider the security implications of storing credentials in plain text.

## Set up locally

1.  **Clone the repository** 

2. **Install `asdf` plugins**
    ```shell
    asdf plugin add python
    asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
    asdf plugin add uv
    ```

3.  **Install tool versions** using `asdf`:
    ```shell
    asdf install
    ```

4.  **Create a virtual environment and install dependencies** using `uv` (now that `asdf` has set the correct Python and `uv` versions):

    ```shell
    uv sync
    ```

5.  **Ensure `uv` is available globally.**
    
    The MCP server can be run from different places so you need `uv` to be available globally. To do so, follow the [official documentation](https://docs.astral.sh/uv/getting-started/installation/).


    > **Tip:** You may need to restart your terminal and/or VS Code for the changes to take effect.

6. Run it locally

    To run your cloned PagerDuty MCP Server you need to update your configuration to use `uv` instead of `uvx`. 

    ```json
    "pagerduty-mcp": { 
        "type": "stdio",
        "command": "uv",
        "args": [
            "run",
            "--directory",
            "/path/to/your/mcp-server-directory",
            // Replace with the full path to the directory where you cloned the MCP server, e.g. "/Users/yourname/code/mcp-server",     
            "python",
            "-m",
            "pagerduty_mcp",
            "--enable-write-tools"
            // This flag enables write operations on the MCP Server enabling you to creating incidents, schedule overrides and much more
        ],
        "env": {
            "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}",
            "PAGERDUTY_API_HOST": "https://api.pagerduty.com"
            // If your PagerDuty account is located in EU update your API host to https://api.eu.pagerduty.com
        }
    }
    ```

## Available Tools and Resources

This section describes the tools provided by the PagerDuty MCP server. They are categorized based on whether they only read data or can modify data in your PagerDuty account.

> **Important:** By default, the MCP server only exposes read-only tools. To enable tools that can modify your PagerDuty account (write-mode tools), you must explicitly start the server with the `--enable-write-tools` flag. This helps prevent accidental changes to your PagerDuty data.

| Tool                   | Area               | Description                                         | Read-only |
|------------------------|--------------------|-----------------------------------------------------|-----------|
| create_alert_grouping_setting | Alert Grouping | Creates a new alert grouping setting                | ❌         |
| delete_alert_grouping_setting | Alert Grouping | Deletes an alert grouping setting                   | ❌         |
| get_alert_grouping_setting    | Alert Grouping | Retrieves a specific alert grouping setting         | ✅         |
| list_alert_grouping_settings  | Alert Grouping | Lists alert grouping settings with filtering        | ✅         |
| update_alert_grouping_setting | Alert Grouping | Updates an existing alert grouping setting          | ❌         |
| get_event_orchestration | Event Orchestrations | Retrieves a specific event orchestration           | ✅         |
| get_event_orchestration_global | Event Orchestrations | Gets the global orchestration configuration for an event orchestration | ✅         |
| get_event_orchestration_router | Event Orchestrations | Gets the router configuration for an event orchestration | ✅         |
| get_event_orchestration_service | Event Orchestrations | Gets the service orchestration configuration for a specific service | ✅         |
| list_event_orchestrations | Event Orchestrations | Lists event orchestrations with optional filtering | ✅         |
| update_event_orchestration_router | Event Orchestrations | Updates the router configuration for an event orchestration | ❌         |
| append_event_orchestration_router_rule | Event Orchestrations | Adds a new routing rule to an event orchestration router | ❌         |
| list_escalation_policies | Escalation Policy  | Lists escalation policies                           | ✅         |
| get_escalation_policy    | Escalation Policy  | Retrieves a specific escalation policy              | ✅         |
| add_note_to_incident     | Incidents          | Adds note to an incident                            | ❌         |
| add_responders           | Incidents          | Adds responders to an incident                      | ❌         |
| create_incident          | Incidents          | Creates a new incident                              | ❌         |
| get_incident             | Incidents          | Retrieves a specific incident                       | ✅         |
| get_outlier_incident     | Incidents          | Retrieves outlier incident information for a specific incident | ✅         |
| get_past_incidents       | Incidents          | Retrieves past incidents related to a specific incident | ✅         |
| get_related_incidents    | Incidents          | Retrieves related incidents for a specific incident | ✅         |
| list_incidents           | Incidents          | Lists incidents                                     | ✅         |
| manage_incidents         | Incidents          | Updates status, urgency, assignment, or escalation level | ❌     |
| get_incident_workflow    | Incident Workflows | Retrieves a specific incident workflow              | ✅         |
| list_incident_workflows  | Incident Workflows | Lists incident workflows with optional filtering    | ✅         |
| start_incident_workflow  | Incident Workflows | Starts a workflow instance for an incident          | ❌         |
| add_team_member          | Teams              | Adds a user to a team with a specific role          | ❌         |
| create_team              | Teams              | Creates a new team                                  | ❌         |
| delete_team              | Teams              | Deletes a team                                      | ❌         |
| get_team                 | Teams              | Retrieves a specific team                           | ✅         |
| list_team_members        | Teams              | Lists members of a team                             | ✅         |
| list_teams               | Teams              | Lists teams                                         | ✅         |
| remove_team_member       | Teams              | Removes a user from a team                          | ❌         |
| update_team              | Teams              | Updates an existing team                            | ❌         |
| get_user_data            | Users              | Gets the current user's data                        | ✅         |
| list_users               | Users              | Lists users in the PagerDuty account                | ✅         |
| list_oncalls             | On-call            | Lists on-call schedules                             | ✅         |
| create_schedule_override | Schedules          | Creates an override for a schedule                  | ❌         |
| get_schedule             | Schedules          | Retrieves a specific schedule                       | ✅         |
| list_schedule_users      | Schedules          | Lists users in a schedule                           | ✅         |
| list_schedules           | Schedules          | Lists schedules                                     | ✅         |
| create_service           | Services           | Creates a new service                               | ❌         |
| get_service              | Services           | Retrieves a specific service                        | ✅         |
| list_services            | Services           | Lists services                                      | ✅         |
| update_service           | Services           | Updates an existing service                         | ❌         |


## Support

PagerDuty's MCP server is an open-source project, and as such, we offer only community-based support. If assistance is required, please open an issue in [GitHub](https://github.com/pagerduty/pagerduty-mcp-server) or [PagerDuty's community forum](https://community.pagerduty.com/).

## Contributing

If you are interested in contributing to this project, please refer to our [Contributing Guidelines](https://github.com/pagerduty/pagerduty-mcp-server/blob/main/CONTRIBUTING.md).
