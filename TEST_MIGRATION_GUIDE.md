# Test Migration Guide: Old @inject_client to New @inject_context Pattern

This guide shows exactly how to fix the remaining test files to work with the new `@inject_context` decorator.

## Current Status

✅ **Working Files** (no changes needed):
- `test_users.py`
- `test_incident_workflows.py`
- `test_status_pages.py`
- `test_event_orchestrations.py`

❌ **Files That Need Fixes**:
- `test_log_entries.py`
- `test_schedules.py` (partially fixed)
- `test_alert_grouping_settings.py` (partially fixed)
- `test_services.py` (partially fixed)
- `test_incidents.py`
- `test_escalation_policies.py`
- `test_change_events.py`
- `test_oncalls.py`
- `test_teams.py`

## Required Changes

### 1. Fix setUp Method

**❌ Old Pattern:**
```python
def setUp(self):
    """Reset mock before each test."""
    self.mock_client.reset_mock()
    # Clear any side effects
    self.mock_client.rget.side_effect = None
    self.mock_client.rpost.side_effect = None
```

**✅ New Pattern:**
```python
def setUp(self):
    """Setup mock context and client for each test."""
    self.mock_client = self.create_mock_client()
    self.mock_context = self.create_mock_context(client=self.mock_client)
```

### 2. Remove @patch Decorators for get_client

**❌ Old Pattern:**
```python
@patch("pagerduty_mcp.tools.services.get_client")
@patch("pagerduty_mcp.tools.services.paginate")
def test_example(self, mock_get_client, mock_paginate):
```

**✅ New Pattern:**
```python
@patch("pagerduty_mcp.tools.services.paginate")
def test_example(self, mock_paginate):
```

### 3. Remove mock_get_client Parameter and Setup

**❌ Old Pattern:**
```python
def test_example(self, mock_get_client, mock_paginate):
    """Test example."""
    mock_get_client.return_value = self.mock_client
    # ... test code
    mock_get_client.assert_called_once()
```

**✅ New Pattern:**
```python
def test_example(self, mock_paginate):
    """Test example."""
    # ... test code (no mock_get_client setup or assertions)
```

### 4. Update Function Calls to Use ctx= Parameter

**❌ Old Pattern:**
```python
result = list_services(ServiceQuery())
result = get_service("SERVICE123")
result = create_service(create_request)
```

**✅ New Pattern:**
```python
result = list_services(ctx=self.mock_context, query_model=ServiceQuery())
result = get_service(ctx=self.mock_context, service_id="SERVICE123")
result = create_service(ctx=self.mock_context, create_request=create_request)
```

## Step-by-Step Process for Each File

1. **Update setUp method** - Replace old reset pattern with ContextTestCase pattern
2. **Remove @patch decorators** - Remove lines like `@patch("...get_client")`
3. **Update method signatures** - Remove `mock_get_client` parameters
4. **Remove mock_get_client code** - Remove setup and assertion lines
5. **Fix function calls** - Add `ctx=self.mock_context` as first parameter
6. **Use correct parameter names** - Check function signatures for proper parameter names

## Function Parameter Names

Common functions and their parameter names:

```python
# Users
get_user_data(ctx=...)  # No other parameters
list_users(ctx=..., query_model=...)

# Services
list_services(ctx=..., query_model=...)
get_service(ctx=..., service_id=...)
create_service(ctx=..., create_request=...)
update_service(ctx=..., service_id=..., update_request=...)

# Teams
list_teams(ctx=..., query_model=...)
get_team(ctx=..., team_id=...)
create_team(ctx=..., create_request=...)

# Schedules
list_schedules(ctx=..., query_model=...)
get_schedule(ctx=..., schedule_id=...)
create_schedule(ctx=..., create_request=...)

# Incidents
list_incidents(ctx=..., query_model=...)
get_incident(ctx=..., incident_id=...)
create_incident(ctx=..., create_request=...)
```

## Example: Complete File Fix

Here's how `test_schedules.py` was fixed:

**Before:**
```python
def setUp(self):
    self.mock_client.reset_mock()
    self.mock_client.rget.side_effect = None

@patch("pagerduty_mcp.tools.schedules.paginate")
def test_list_schedules_no_filters(self, mock_get_client, mock_paginate):
    mock_get_client.return_value = self.mock_client
    mock_paginate.return_value = self.sample_schedules_list_response

    query = ScheduleQuery()
    result = list_schedules(query)  # Wrong!

    mock_get_client.assert_called_once()
```

**After:**
```python
def setUp(self):
    self.mock_client = self.create_mock_client()
    self.mock_context = self.create_mock_context(client=self.mock_client)

@patch("pagerduty_mcp.tools.schedules.paginate")
def test_list_schedules_no_filters(self, mock_paginate):
    mock_paginate.return_value = self.sample_schedules_list_response

    query = ScheduleQuery()
    result = list_schedules(ctx=self.mock_context, query_model=query)  # Correct!

    # No mock_get_client assertions needed
```

## Verification

After making changes, run tests to verify:
```bash
# Test a specific file
uv run python -m pytest tests/test_schedules.py -v

# Test all files
make test
```

## Quick Analysis Command

To see what needs fixing in any file:
```bash
python scripts/analyze_tests.py
```

The goal is to get all 308 tests passing with the new dependency injection pattern!