# Schedule Creation Implementation Guide

This guide outlines the step-by-step process for implementing the schedule creation feature in the PagerDuty MCP Server. Follow these steps to complete the implementation while working on the `feature/add-schedule-creation` branch.

## 1. Feature Implementation Steps

### 1.1 Update Models

First, create or update the necessary models in `/pagerduty_mcp/models/schedules.py`:

1. Add a `ScheduleLayerRestriction` model:
   ```python
   class ScheduleLayerRestriction(BaseModel):
       type: str = Field(description="The type of restriction (daily_restriction or weekly_restriction)")
       start_time_of_day: str = Field(description="The time of day when the restriction starts (HH:MM:SS)")
       duration_seconds: int = Field(description="The duration of the restriction in seconds")
       start_day_of_week: int | None = Field(
           default=None,
           description="The day of week the restriction starts (only for weekly_restriction)",
       )
   ```

2. Add a `ScheduleLayerCreate` model:
   ```python
   class ScheduleLayerCreate(BaseModel):
       name: str = Field(description="The name of the schedule layer")
       start: datetime = Field(description="The start time of this layer")
       end: datetime | None = Field(
           default=None,
           description="The end time of this layer. If null, the layer does not end",
       )
       rotation_virtual_start: datetime = Field(
           description="The effective start time of the layer. This can be before the start time of the schedule"
       )
       rotation_turn_length_seconds: int = Field(description="The duration of each on-call shift in seconds")
       users: list[ScheduleLayerUser] = Field(
           description="The ordered list of users on this layer. The position of the user on the list "
           "determines their order in the layer"
       )
       restrictions: list[ScheduleLayerRestriction] | None = Field(
           default=None,
           description="An array of restrictions for the layer. A restriction is a limit on which "
           "period of the day or week the schedule layer can accept assignments",
       )
   ```

3. Add the schedule creation models:
   ```python
   class ScheduleCreateData(BaseModel):
       name: str = Field(description="The name of the schedule")
       time_zone: str = Field(description="The time zone of the schedule (e.g., America/New_York)")
       description: str | None = Field(default=None, description="The description of the schedule")
       schedule_layers: list[ScheduleLayerCreate] = Field(description="A list of schedule layers")
       type: Literal["schedule"] = "schedule"

   class ScheduleCreateRequest(BaseModel):
       schedule: ScheduleCreateData = Field(
           description="The schedule to be created",
       )
   ```

4. Update the imports at the top of the file as needed.

### 1.2 Add the Tool Function

Add the `create_schedule` function to `/pagerduty_mcp/tools/schedules.py`:

```python
def create_schedule(create_model: ScheduleCreateRequest) -> Schedule:
    """Create a new on-call schedule.
    
    Args:
        create_model: The schedule creation data
        
    Returns:
        The created schedule
    """
    # Convert datetime objects to ISO 8601 strings for all schedule layers
    request_data = create_model.model_dump()
    for layer in request_data["schedule"]["schedule_layers"]:
        layer["start"] = layer["start"].isoformat()
        if layer["end"] is not None:
            layer["end"] = layer["end"].isoformat()
        layer["rotation_virtual_start"] = layer["rotation_virtual_start"].isoformat()

    # Send request to PagerDuty API
    response = get_client().rpost("/schedules", json=request_data)

    # Handle different response formats
    if type(response) is dict and "schedule" in response:
        return Schedule.model_validate(response["schedule"])

    return Schedule.model_validate(response)
```

### 1.3 Register the Tool

Update `/pagerduty_mcp/tools/__init__.py` to import and register the new tool:

1. Add the import:
   ```python
   from .schedules import (
       create_schedule,  # Add this import
       create_schedule_override,
       get_schedule,
       list_schedule_users,
       list_schedules,
   )
   ```

2. Add the tool to the `write_tools` list:
   ```python
   # Write tools (potentially dangerous operations that modify state)
   write_tools = [
       # Existing tools...
       create_schedule,  # Add this line
       # Other existing tools...
   ]
   ```

### 1.4 Update Model Exports (If Needed)

Update the model exports in `/pagerduty_mcp/models/__init__.py` to include the new models if they need to be exposed outside the module.

## 2. Testing

### 2.1 Add Unit Tests

Add tests to `/tests/test_schedules.py` to verify the new functionality:

1. Add a test for successful schedule creation:
   ```python
   @patch("pagerduty_mcp.tools.schedules.get_client")
   def test_create_schedule_success(self, mock_get_client):
       """Test successful schedule creation."""
       mock_get_client.return_value = self.mock_client
       
       # Create a mock response
       mock_response = {"schedule": self.sample_schedule_response}
       self.mock_client.rpost.return_value = mock_response
       
       # Create test data
       # (Create a ScheduleCreateRequest instance with test data)
       
       result = create_schedule(request)
       
       # Verify API call
       mock_get_client.assert_called_once()
       self.mock_client.rpost.assert_called_once()
       
       # Verify result
       self.assertIsInstance(result, Schedule)
       # Add more assertions
   ```

2. Add a test for handling API errors:
   ```python
   @patch("pagerduty_mcp.tools.schedules.get_client")
   def test_create_schedule_api_error(self, mock_get_client):
       """Test create_schedule when API returns an error."""
       mock_get_client.return_value = self.mock_client
       self.mock_client.rpost.side_effect = Exception("API Error")
       
       # Create test data
       
       with self.assertRaises(Exception) as context:
           create_schedule(request)
       
       self.assertEqual(str(context.exception), "API Error")
   ```

3. Add more tests as needed to cover different scenarios.

### 2.2 Run the Tests

Run the tests to verify your implementation:

```bash
pytest tests/test_schedules.py
```

## 3. Git Workflow

### 3.1 Committing Changes

Commit your changes regularly with descriptive messages:

```bash
# After implementing models
git add pagerduty_mcp/models/schedules.py
git commit -m "feat: add schedule creation models"

# After implementing the tool function
git add pagerduty_mcp/tools/schedules.py
git commit -m "feat: add create_schedule tool function"

# After registering the tool
git add pagerduty_mcp/tools/__init__.py
git commit -m "feat: register create_schedule tool"

# After adding tests
git add tests/test_schedules.py
git commit -m "test: add unit tests for schedule creation"
```

### 3.2 Pushing to a Remote Repository (Optional)

If you want to share your branch with others or back it up, you can push it to a remote repository:

```bash
git push -u origin feature/add-schedule-creation
```

This creates a new branch on the remote repository and sets up tracking.

## 4. Creating a Pull Request

When you've completed and tested the feature, you can create a pull request:

1. Push your branch to the remote repository if you haven't already:
   ```bash
   git push -u origin feature/add-schedule-creation
   ```

2. Go to the GitHub repository in your web browser.

3. You should see a prompt to create a pull request for your recently pushed branch. Click on it.

4. Fill in the pull request details:
   - Title: "Add schedule creation support"
   - Description: Include a summary of changes, reference to any issues, and testing notes
   - Reviewers: Add any team members who should review the code

5. Submit the pull request.

6. Address any feedback from code reviews by making additional commits to your branch.

## 5. Tips for Implementation

1. **Use Existing Patterns**: Follow the patterns established in other similar operations like `create_service`.

2. **Handle Dates Properly**: Ensure all datetime objects are properly converted to ISO 8601 strings.

3. **Error Handling**: Include appropriate error handling, especially for API responses.

4. **Documentation**: Add thorough docstrings to all new functions and models.

5. **Testing**: Write comprehensive tests covering both success and error cases.

Good luck with the implementation!