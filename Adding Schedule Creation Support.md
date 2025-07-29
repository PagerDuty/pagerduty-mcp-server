# Adding Schedule Creation Support to PagerDuty MCP Server

This document outlines the requirements and implementation plan for adding schedule creation capability to the PagerDuty MCP Server. The implementation will follow the patterns and guidelines established in the Golden Template document.

## 1. Overview and Requirements

### 1.1 Current State Assessment

The PagerDuty MCP Server currently supports several schedule operations:
- Listing schedules with filtering (`list_schedules`)
- Retrieving a specific schedule by ID (`get_schedule`)
- Creating schedule overrides (`create_schedule_override`)
- Listing users in a schedule (`list_schedule_users`)

However, it lacks the ability to create new schedules, which is a key operation for programmatic schedule management.

### 1.2 PagerDuty API Requirements

Based on the PagerDuty API documentation, creating a schedule requires a POST request to `/schedules` with the following key components:

1. **Core Schedule Properties**:
   - `name` (required): The name of the schedule
   - `time_zone` (required): The time zone for the schedule (e.g., "America/New_York")
   - `description` (optional): A description of the schedule
   - `type` (fixed): Always "schedule"

2. **Schedule Layers**:
   Each schedule must have at least one layer, which defines the rotation pattern. A layer includes:
   - `name`: The name of the layer
   - `start`: ISO 8601 timestamp when the layer begins
   - `rotation_virtual_start`: ISO 8601 timestamp for the start of the rotation
   - `rotation_turn_length_seconds`: Duration of each user's shift in seconds
   - `users`: Array of user references to include in the rotation
   - `restrictions` (optional): Time-based restrictions on when the layer is active

3. **User References**:
   Users in schedule layers are referenced by:
   - `id`: The user's PagerDuty ID
   - `type`: Always "user_reference"

### 1.3 Integration Requirements

The new schedule creation functionality must:
1. Follow the existing MCP Server patterns and architecture
2. Be properly registered as a write operation (destructive)
3. Include appropriate validations and error handling
4. Be thoroughly tested with unit tests
5. Support all schedule creation features of the PagerDuty API

## 2. Implementation Plan

### 2.1 Model Definitions

#### 2.1.1 Schedule Layer User Model

The `ScheduleLayerUser` model already exists and can be reused:

```python
class ScheduleLayerUser(BaseModel):
    user: UserReference = Field(description="The reference to the user in this layer")
```

#### 2.1.2 Restriction Model

A new model for schedule layer restrictions is needed:

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

#### 2.1.3 Schedule Layer Create Model

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

#### 2.1.4 Schedule Create Models

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

### 2.2 Tool Implementation

A new tool function will be added to `pagerduty_mcp/tools/schedules.py`:

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

### 2.3 Tool Registration

The new tool will be registered in `pagerduty_mcp/tools/__init__.py`:

```python
from .schedules import (
    create_schedule,  # Add this import
    create_schedule_override,
    get_schedule,
    list_schedule_users,
    list_schedules,
)

# Write tools (potentially dangerous operations that modify state)
write_tools = [
    # Existing tools...
    # Add the new tool:
    create_schedule,
    # Other existing tools...
]
```

## 3. Testing Strategy

### 3.1 Unit Tests

New unit tests will be added to `tests/test_schedules.py` following the existing patterns:

```python
def test_create_schedule_success(self, mock_get_client):
    """Test successful schedule creation."""
    mock_get_client.return_value = self.mock_client
    
    # Create a mock response similar to the API's actual response
    mock_response = {"schedule": self.sample_schedule_response}
    self.mock_client.rpost.return_value = mock_response
    
    # Create a test schedule request
    layer = ScheduleLayerCreate(
        name="Night Shift",
        start=datetime(2023, 1, 1, 20, 0),
        rotation_virtual_start=datetime(2023, 1, 1, 20, 0),
        rotation_turn_length_seconds=86400,
        users=[ScheduleLayerUser(user=UserReference(id="USER123", summary="John Doe"))]
    )
    
    schedule_data = ScheduleCreateData(
        name="Engineering On-Call",
        time_zone="America/New_York",
        description="Primary engineering on-call rotation",
        schedule_layers=[layer]
    )
    
    request = ScheduleCreateRequest(schedule=schedule_data)
    
    result = create_schedule(request)
    
    # Verify API call was made correctly
    mock_get_client.assert_called_once()
    
    # Verify result
    self.assertIsInstance(result, Schedule)
    self.assertEqual(result.id, "SCHED123")
    self.assertEqual(result.name, "Web Application Service")
```

Additional tests will cover:
1. Error handling (API errors)
2. Complex schedules with multiple layers
3. Schedules with restrictions
4. Different response formats

## 4. Common Schedule Patterns and Use Cases

### 4.1 24/7 Follow-the-Sun Rotation

A continuous rotation where team members take turns for a day at a time:

```python
users = [
    ScheduleLayerUser(user=UserReference(id="USER1")),
    ScheduleLayerUser(user=UserReference(id="USER2")),
    ScheduleLayerUser(user=UserReference(id="USER3")),
]

layer = ScheduleLayerCreate(
    name="Follow-the-Sun",
    start=datetime.now(),
    rotation_virtual_start=datetime.now(),
    rotation_turn_length_seconds=86400,  # 24 hours
    users=users,
)

schedule = ScheduleCreateData(
    name="24x7 Engineering Support",
    time_zone="UTC",
    description="Round-the-clock coverage",
    schedule_layers=[layer]
)
```

### 4.2 Business Hours Coverage with Restrictions

A schedule that only covers business hours:

```python
restriction = ScheduleLayerRestriction(
    type="daily_restriction",
    start_time_of_day="09:00:00",
    duration_seconds=28800,  # 8 hours
)

layer = ScheduleLayerCreate(
    name="Business Hours",
    start=datetime.now(),
    rotation_virtual_start=datetime.now(),
    rotation_turn_length_seconds=604800,  # 1 week
    users=[ScheduleLayerUser(user=UserReference(id="USER1"))],
    restrictions=[restriction]
)
```

### 4.3 Weekly Rotation with Weekend Restrictions

A weekly rotation that excludes weekend coverage:

```python
# Monday through Friday
weekday_restrictions = [
    ScheduleLayerRestriction(
        type="weekly_restriction",
        start_day_of_week=1,  # Monday
        start_time_of_day="09:00:00",
        duration_seconds=28800,  # 8 hours
    ),
    ScheduleLayerRestriction(
        type="weekly_restriction",
        start_day_of_week=2,  # Tuesday
        start_time_of_day="09:00:00",
        duration_seconds=28800,
    ),
    # Wednesday, Thursday, Friday similarly
]

layer = ScheduleLayerCreate(
    name="Weekday Coverage",
    start=datetime.now(),
    rotation_virtual_start=datetime.now(),
    rotation_turn_length_seconds=604800,  # 1 week
    users=[ScheduleLayerUser(user=UserReference(id="USER1"))],
    restrictions=weekday_restrictions
)
```

## 5. Implementation Considerations

### 5.1 Datetime Handling

The PagerDuty API expects ISO 8601 formatted datetime strings, so all datetime objects need to be converted before sending the request. The implementation must handle timezone information correctly.

### 5.2 Validation

The schedule creation tool should validate that:
1. At least one schedule layer is provided
2. Each layer has at least one user
3. Time zone is a valid IANA time zone identifier
4. Required fields are provided

### 5.3 Error Handling

The tool should gracefully handle API errors and provide meaningful error messages to users.

## 6. Conclusion

Adding schedule creation support to the PagerDuty MCP Server will significantly enhance its capabilities, allowing programmatic management of on-call schedules. The implementation follows established patterns in the codebase and maintains consistency with the PagerDuty API's requirements.