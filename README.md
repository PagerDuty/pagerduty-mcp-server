# PagerDuty's official MCP Server

<!-- mcp-name: io.github.PagerDuty/pagerduty-mcp -->

PagerDuty's local MCP (Model Context Protocol) server which provides tools to interact with your PagerDuty account, allowing you to manage incidents, services, schedules, event orchestrations, and more directly from your MCP-enabled client.

## 🎉 v2.0 - Multi-Server Architecture

**New in v2.0**: PagerDuty MCP now provides **4 independent servers**, one per product category, for better organization and smaller LLM contexts:

- **`pagerduty-incidents`** - Incident management (9 tools)
- **`pagerduty-services`** - Service configuration (4 tools)
- **`pagerduty-people`** - Teams, users, schedules, on-calls (17 tools)
- **`pagerduty-aiops`** - Alert grouping and event orchestrations (12 tools)

**Benefits:**
- ✅ Smaller, focused tool sets per server
- ✅ Granular control over which capabilities you need
- ✅ Better LLM performance with reduced context
- ✅ Independent write permissions per server

**Note:** The monolithic `pagerduty-mcp` command is still available for backward compatibility but will be removed in v2.1.

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

### v2.0 Multi-Server Configuration (Recommended)

Configure multiple independent servers to use only the capabilities you need. Here's an example with all 4 servers:

```json
{
  "mcpServers": {
    "pagerduty-incidents": {
      "type": "stdio",
      "command": "uvx",
      "args": ["pagerduty-incidents", "--enable-write-tools"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}"
      }
    },
    "pagerduty-people": {
      "type": "stdio",
      "command": "uvx",
      "args": ["pagerduty-people"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}"
      }
    },
    "pagerduty-aiops": {
      "type": "stdio",
      "command": "uvx",
      "args": ["pagerduty-aiops", "--enable-write-tools"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}"
      }
    },
    "pagerduty-services": {
      "type": "stdio",
      "command": "uvx",
      "args": ["pagerduty-services"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}"
      }
    }
  }
}
```

**You can configure just the servers you need!** For example, if you only need incident management:

```json
{
  "mcpServers": {
    "pagerduty-incidents": {
      "type": "stdio",
      "command": "uvx",
      "args": ["pagerduty-incidents", "--enable-write-tools"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}"
      }
    }
  }
}
```

### v1.x Monolithic Configuration (Deprecated)

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

    To run your cloned PagerDuty MCP Server locally, you need to update your configuration to use `uv run` with the `--directory` flag pointing to your local clone.

    **For v2.0 Multi-Server Architecture (Recommended):**

    Configure each server independently, pointing to your local directory:

    ```json
    {
      "mcpServers": {
        "pagerduty-incidents-dev": {
          "type": "stdio",
          "command": "uv",
          "args": [
            "run",
            "--directory",
            "/path/to/your/pagerduty-mcp-server",
            // Replace with the full path to your cloned repository
            "python",
            "-m",
            "pagerduty_mcp.servers.incidents",
            "--enable-write-tools"
          ],
          "env": {
            "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}",
            "PAGERDUTY_API_HOST": "https://api.pagerduty.com"
          }
        },
        "pagerduty-services-dev": {
          "type": "stdio",
          "command": "uv",
          "args": [
            "run",
            "--directory",
            "/path/to/your/pagerduty-mcp-server",
            "python",
            "-m",
            "pagerduty_mcp.servers.services"
          ],
          "env": {
            "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}"
          }
        },
        "pagerduty-people-dev": {
          "type": "stdio",
          "command": "uv",
          "args": [
            "run",
            "--directory",
            "/path/to/your/pagerduty-mcp-server",
            "python",
            "-m",
            "pagerduty_mcp.servers.people",
            "--enable-write-tools"
          ],
          "env": {
            "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}"
          }
        },
        "pagerduty-aiops-dev": {
          "type": "stdio",
          "command": "uv",
          "args": [
            "run",
            "--directory",
            "/path/to/your/pagerduty-mcp-server",
            "python",
            "-m",
            "pagerduty_mcp.servers.aiops",
            "--enable-write-tools"
          ],
          "env": {
            "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}"
          }
        }
      }
    }
    ```

    **For v1.x Monolithic Server (Deprecated):**

    ```json
    "pagerduty-mcp-dev": {
        "type": "stdio",
        "command": "uv",
        "args": [
            "run",
            "--directory",
            "/path/to/your/pagerduty-mcp-server",
            "python",
            "-m",
            "pagerduty_mcp",
            "--enable-write-tools"
        ],
        "env": {
            "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}",
            "PAGERDUTY_API_HOST": "https://api.pagerduty.com"
        }
    }
    ```

    **Using MCP Inspector for Interactive Testing:**

    The MCP Inspector provides a web UI for testing servers during development:

    ```bash
    # Test individual servers
    npx @modelcontextprotocol/inspector uv run python -m pagerduty_mcp.servers.incidents --enable-write-tools
    npx @modelcontextprotocol/inspector uv run python -m pagerduty_mcp.servers.services
    npx @modelcontextprotocol/inspector uv run python -m pagerduty_mcp.servers.people
    npx @modelcontextprotocol/inspector uv run python -m pagerduty_mcp.servers.aiops --enable-write-tools

    # Or use the make command (see Development section)
    make debug SERVER=incidents
    ```

## Development

### Adding a New Server

To add a new server to the multi-server architecture, follow this pattern:

1. **Create the server directory structure:**

   ```bash
   mkdir -p pagerduty_mcp/servers/your-server
   cd pagerduty_mcp/servers/your-server
   ```

2. **Create the required files:**

   - `__init__.py` - Package initialization with exports
   - `__main__.py` - Entry point for the CLI command
   - `models.py` - Pydantic models for your domain
   - `tools.py` - Tool functions and tool lists (READ_TOOLS, WRITE_TOOLS)
   - `server.py` - FastMCP server configuration

3. **Implement `models.py`:**

   ```python
   """Models for Your Server."""
   from pydantic import BaseModel, Field
   # Add your Pydantic models here
   ```

4. **Implement `tools.py`:**

   ```python
   """Tools for Your Server MCP Server."""
   from pagerduty_mcp.common import get_client, paginate
   from pagerduty_mcp.models import ListResponseModel
   from .models import YourModel

   def your_read_tool(param: str) -> YourModel:
       """Tool description for LLM."""
       # Implementation
       pass

   def your_write_tool(param: str) -> YourModel:
       """Tool description for LLM."""
       # Implementation
       pass

   # Tool lists for registration
   READ_TOOLS = [your_read_tool]
   WRITE_TOOLS = [your_write_tool]
   ```

5. **Implement `server.py`:**

   ```python
   """Your Server MCP Server."""
   import typer
   from pagerduty_mcp.common import (
       create_pagerduty_server,
       register_read_tools,
       register_write_tools,
   )
   from .tools import READ_TOOLS, WRITE_TOOLS

   INSTRUCTIONS = """
   # Your Server MCP Server

   Description of what this server does...
   """

   app = typer.Typer()

   @app.command()
   def run(*, enable_write_tools: bool = False):
       """Run Your Server MCP Server."""
       mcp = create_pagerduty_server(
           name="Your Server MCP Server",
           instructions=INSTRUCTIONS,
       )
       register_read_tools(mcp, READ_TOOLS)
       if enable_write_tools:
           register_write_tools(mcp, WRITE_TOOLS)
       mcp.run()

   if __name__ == "__main__":
       app()
   ```

6. **Implement `__main__.py`:**

   ```python
   """Entry point for Your Server MCP Server."""
   from .server import app

   def main():
       """Main entry point for pagerduty-your-server command."""
       print("Starting Your Server MCP Server...")
       print("Note: Use --enable-write-tools to enable modifications.")
       app()

   if __name__ == "__main__":
       main()
   ```

7. **Implement `__init__.py`:**

   ```python
   """Your Server MCP Server."""
   from .server import app
   __all__ = ["app"]
   ```

8. **Add entry point to `pyproject.toml`:**

   ```toml
   [project.scripts]
   pagerduty-your-server = "pagerduty_mcp.servers.your_server.__main__:main"
   ```

9. **Install and test:**

   ```bash
   uv sync
   uv run pagerduty-your-server --help
   npx @modelcontextprotocol/inspector uv run python -m pagerduty_mcp.servers.your_server
   ```

10. **Add tests** in `tests/servers/your_server/` following the pattern of existing server tests.

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run linting
make lint

# Format code
make format
```

## Available Tools and Resources

This section describes the tools provided by the PagerDuty MCP servers. In v2.0, tools are organized into independent servers by product area.

> **Important:** By default, all MCP servers only expose read-only tools. To enable tools that can modify your PagerDuty account (write-mode tools), you must explicitly start each server with the `--enable-write-tools` flag. This helps prevent accidental changes to your PagerDuty data.

### Server Distribution by Area

The following table shows which server provides tools for each PagerDuty area:

| Server | Area | Description |
|--------|------|-------------|
| **pagerduty-aiops** | AIOps - Alert Grouping | Noise reduction through intelligent alert grouping settings |
| **pagerduty-aiops** | AIOps - Event Orchestrations | Event routing and orchestration rules configuration |
| **pagerduty-people** | Escalation Policies | Escalation policy management and configuration |
| **pagerduty-incidents** | Incidents | Incident management, creation, updates, and analysis |
| **pagerduty-incidents** | Incidents - Insights | Outlier detection, past incidents, and related incidents analysis |
| **pagerduty-incidents** | Incidents - Response | Responder management and incident notes |
| **pagerduty-people** | On-call | On-call schedule viewing and management |
| **pagerduty-people** | Schedules | Schedule management, users, and overrides |
| **pagerduty-services** | Services | Service directory, creation, and configuration |
| **pagerduty-people** | Teams | Team management, members, and roles |
| **pagerduty-people** | Users | User information and directory |

### Tool Details by Server

#### pagerduty-aiops (12 tools)
**Areas:** AIOps - Alert Grouping, Event Orchestrations

| Tool | Area | Description | Read-only |
|------|------|-------------|-----------|
| list_alert_grouping_settings | Alert Grouping | Lists alert grouping settings with filtering | ✅ |
| get_alert_grouping_setting | Alert Grouping | Retrieves a specific alert grouping setting | ✅ |
| create_alert_grouping_setting | Alert Grouping | Creates a new alert grouping setting | ❌ |
| update_alert_grouping_setting | Alert Grouping | Updates an existing alert grouping setting | ❌ |
| delete_alert_grouping_setting | Alert Grouping | Deletes an alert grouping setting | ❌ |
| list_event_orchestrations | Event Orchestrations | Lists event orchestrations with optional filtering | ✅ |
| get_event_orchestration | Event Orchestrations | Retrieves a specific event orchestration | ✅ |
| get_event_orchestration_router | Event Orchestrations | Gets the router configuration for an event orchestration | ✅ |
| get_event_orchestration_service | Event Orchestrations | Gets the service orchestration configuration for a specific service | ✅ |
| get_event_orchestration_global | Event Orchestrations | Gets the global orchestration configuration | ✅ |
| update_event_orchestration_router | Event Orchestrations | Updates the router configuration for an event orchestration | ❌ |
| append_event_orchestration_router_rule | Event Orchestrations | Adds a new routing rule to an event orchestration router | ❌ |

#### pagerduty-incidents (9 tools)
**Areas:** Incidents, Incident Insights, Incident Response

| Tool | Area | Description | Read-only |
|------|------|-------------|-----------|
| list_incidents | Incidents | Lists incidents with filtering options | ✅ |
| get_incident | Incidents | Retrieves a specific incident | ✅ |
| get_outlier_incident | Incidents | Retrieves outlier incident information | ✅ |
| get_past_incidents | Incidents | Retrieves past incidents related to a specific incident | ✅ |
| get_related_incidents | Incidents | Retrieves related incidents for a specific incident | ✅ |
| create_incident | Incidents | Creates a new incident | ❌ |
| manage_incidents | Incidents | Updates status, urgency, assignment, or escalation level | ❌ |
| add_responders | Incidents | Adds responders to an incident | ❌ |
| add_note_to_incident | Incidents | Adds note to an incident | ❌ |

#### pagerduty-people (17 tools)
**Areas:** Users, Teams, Schedules, On-call, Escalation Policies

| Tool | Area | Description | Read-only |
|------|------|-------------|-----------|
| get_user_data | Users | Gets the current user's data | ✅ |
| list_users | Users | Lists users in the PagerDuty account | ✅ |
| list_teams | Teams | Lists teams | ✅ |
| get_team | Teams | Retrieves a specific team | ✅ |
| list_team_members | Teams | Lists members of a team | ✅ |
| create_team | Teams | Creates a new team | ❌ |
| update_team | Teams | Updates an existing team | ❌ |
| delete_team | Teams | Deletes a team | ❌ |
| add_team_member | Teams | Adds a user to a team with a specific role | ❌ |
| remove_team_member | Teams | Removes a user from a team | ❌ |
| list_schedules | Schedules | Lists schedules | ✅ |
| get_schedule | Schedules | Retrieves a specific schedule | ✅ |
| list_schedule_users | Schedules | Lists users in a schedule | ✅ |
| create_schedule_override | Schedules | Creates an override for a schedule | ❌ |
| list_oncalls | On-call | Lists on-call schedules | ✅ |
| list_escalation_policies | Escalation Policies | Lists escalation policies | ✅ |
| get_escalation_policy | Escalation Policies | Retrieves a specific escalation policy | ✅ |

#### pagerduty-services (4 tools)
**Areas:** Services

| Tool | Area | Description | Read-only |
|------|------|-------------|-----------|
| list_services | Services | Lists services | ✅ |
| get_service | Services | Retrieves a specific service | ✅ |
| create_service | Services | Creates a new service | ❌ |
| update_service | Services | Updates an existing service | ❌ |


## Support

PagerDuty's MCP server is an open-source project, and as such, we offer only community-based support. If assistance is required, please open an issue in [GitHub](https://github.com/pagerduty/pagerduty-mcp-server) or [PagerDuty's community forum](https://community.pagerduty.com/).

## Contributing

If you are interested in contributing to this project, please refer to our [Contributing Guidelines](https://github.com/pagerduty/pagerduty-mcp-server/blob/main/CONTRIBUTING.md).
