# Golden Template and Requirements for Extending PagerDuty MCP Server

This document provides comprehensive guidelines and templates for extending the PagerDuty MCP Server with new operations. It's based on analysis of the existing codebase and identifies consistent patterns used throughout the implementation.

## 1. Architecture Overview

The PagerDuty MCP (Model Context Protocol) Server follows a well-structured architecture that separates concerns into distinct layers:

### 1.1 Core Architecture

```
pagerduty_mcp/
├── __init__.py
├── __main__.py       # Entry point
├── client.py         # PagerDuty API client 
├── models/           # Data models (Pydantic)
├── server.py         # MCP server configuration
├── tools/            # Tool implementations
└── utils.py          # Utility functions
```

### 1.2 Key Design Patterns

1. **Separation of Read and Write Operations**:
   - Read operations (get/list) are safe, non-destructive and enabled by default
   - Write operations (create/update/delete) are potentially destructive and disabled by default
   - The server requires an explicit `--enable-write-tools` flag to expose write operations

2. **Layered Architecture**:
   - **Models Layer**: Pydantic models for request/response validation
   - **Tools Layer**: Tool implementations that use the models and client
   - **Server Layer**: Registers tools with the MCP framework

3. **Consistent Naming Conventions**:
   - Read Operations: `list_[entity]` or `get_[entity]`
   - Write Operations: `create_[entity]`, `update_[entity]`, `delete_[entity]`
   - Models: `[Entity]`, `[Entity]Query`, `[Entity]Create`, `[Entity]Reference`

## 2. Model Definition Templates

Models in PagerDuty MCP Server follow consistent patterns using Pydantic. There are several common model types that appear throughout the codebase.

### 2.1 Base Models and References

The base models provide common patterns for references and list responses:

```python
# Example based on references.py
class ReferenceBase(BaseModel):
    id: str = Field(description="The ID of the referenced object")
    summary: str | None = Field(
        default=None,
        description="A short-form, server-generated string that provides succinct information about the referenced object",
    )

    _type: ClassVar[str]

    @computed_field
    @property
    def type(self) -> str:
        return self._type

# Entity-specific references inherit from ReferenceBase
class EntityNameReference(ReferenceBase):
    _type: ClassVar[str] = "entity_name_reference"
```

### 2.2 Entity Model Template

Primary entity models represent the core resources:

```python
# Example based on teams.py and services.py
class EntityName(BaseModel):
    id: str | None = Field(description="The ID of the entity", default=None)
    name: str | None = Field(default=None, description="The name of the entity")
    description: str | None = Field(default=None, description="The description of the entity")
    # Entity-specific fields here
    
    @computed_field
    @property
    def type(self) -> Literal["entity_type"]:
        return "entity_type"
```

### 2.3 Query Model Template

Query models are used for list operations and define filtering parameters:

```python
# Example based on teams.py and services.py
class EntityNameQuery(BaseModel):
    query: str | None = Field(
        description="Filters the result, showing only the records whose name matches the query",
        default=None,
    )
    # Entity-specific filter fields here
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Pagination limit",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.query:
            params["query"] = self.query
        if self.limit:
            params["limit"] = self.limit
        # Add entity-specific parameter transforms
        return params
```

### 2.4 Create/Update Model Template

Models for creating or updating entities:

```python
# Example based on teams.py and services.py
class EntityNameCreate(BaseModel):
    name: str
    description: str | None = Field(
        default=None,
        description="Description of the entity",
    )
    # Additional fields specific to entity creation

class EntityNameCreateRequest(BaseModel):
    entity_name: EntityNameCreate = Field(
        description="The entity to create",
    )
```

## 3. Tool Implementation Templates

Tools are the primary interface for MCP clients to interact with the PagerDuty API. There are consistent patterns for both read and write operations.

### 3.1 Read Operation Template (List)

```python
# Example based on teams.py and services.py
def list_entity_names(query_model: EntityNameQuery) -> ListResponseModel[EntityName]:
    """List entity names based on provided query parameters.

    Args:
        query_model: The model containing the query parameters
    Returns:
        List of entity names matching the query.
    """
    response = paginate(client=get_client(), entity="entity_names", params=query_model.to_params())
    entities = [EntityName(**entity) for entity in response]
    return ListResponseModel[EntityName](response=entities)
```

### 3.2 Read Operation Template (Get)

```python
# Example based on teams.py and services.py
def get_entity_name(entity_id: str) -> EntityName:
    """Get a specific entity.

    Args:
        entity_id: The ID of the entity to retrieve
    Returns:
        Entity details
    """
    response = get_client().rget(f"/entity_names/{entity_id}")
    return EntityName.model_validate(response)
```

### 3.3 Write Operation Template (Create)

```python
# Example based on teams.py and services.py
def create_entity_name(create_model: EntityNameCreateRequest) -> EntityName:
    """Create a new entity.

    Args:
        create_model: The data for the new entity
    Returns:
        The created entity
    """
    response = get_client().rpost("/entity_names", json=create_model.model_dump())

    # Handle different response formats
    if type(response) is dict and "entity_name" in response:
        return EntityName.model_validate(response["entity_name"])

    return EntityName.model_validate(response)
```

### 3.4 Write Operation Template (Update)

```python
# Example based on teams.py and services.py
def update_entity_name(entity_id: str, update_model: EntityNameCreateRequest) -> EntityName:
    """Update an existing entity.

    Args:
        entity_id: The ID of the entity to update
        update_model: The updated entity data
    Returns:
        The updated entity
    """
    response = get_client().rput(f"/entity_names/{entity_id}", json=update_model.model_dump())

    # Handle different response formats
    if type(response) is dict and "entity_name" in response:
        return EntityName.model_validate(response["entity_name"])

    return EntityName.model_validate(response)
```

### 3.5 Write Operation Template (Delete)

```python
# Example based on teams.py
def delete_entity_name(entity_id: str) -> None:
    """Delete an entity.

    Args:
        entity_id: The ID of the entity to delete
    """
    get_client().rdelete(f"/entity_names/{entity_id}")
    # The API typically doesn't return content for successful deletion
```

### 3.6 Common Utility Functions

```python
# For paginated results
def paginate(*, client: RestApiV2Client, entity: str, params: dict, maximum_records: int = MAX_RESULTS):
    """Paginate through API results with early termination."""
    results = []
    count = 0
    for item in client.iter_all(entity, params=params):
        results.append(item)
        count += 1
        if count >= maximum_records:
            break
    return results
```

## 4. Testing Strategy

The PagerDuty MCP Server uses a comprehensive testing strategy that includes unit tests and competency tests.

### 4.1 Unit Test Template for Tools

```python
# Example based on test_teams.py and test_services.py
class TestEntityNameTools(unittest.TestCase):
    """Test cases for entity name tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_entity_response = {
            "id": "ENTITY123",
            "name": "Sample Entity",
            "description": "Description of sample entity",
            # Other entity fields
        }

        cls.sample_entities_list_response = [
            cls.sample_entity_response,
            {
                "id": "ENTITY456",
                "name": "Another Entity",
                # Other entity fields
            },
        ]

        cls.mock_client = MagicMock()

    def setUp(self):
        """Reset mock before each test."""
        self.mock_client.reset_mock()
        # Clear any side effects
        self.mock_client.rget.side_effect = None
        self.mock_client.rpost.side_effect = None
        self.mock_client.rput.side_effect = None
        self.mock_client.rdelete.side_effect = None

    @patch("pagerduty_mcp.tools.entity_names.paginate")
    @patch("pagerduty_mcp.tools.entity_names.get_client")
    def test_list_entities(self, mock_get_client, mock_paginate):
        """Test listing entities."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_entities_list_response

        query = EntityNameQuery()
        result = list_entity_names(query)

        # Verify paginate call
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="entity_names", params=query.to_params()
        )

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], EntityName)
        self.assertEqual(result.response[0].id, "ENTITY123")
        self.assertEqual(result.response[1].id, "ENTITY456")

    @patch("pagerduty_mcp.tools.entity_names.get_client")
    def test_get_entity(self, mock_get_client):
        """Test getting a specific entity."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_entity_response

        result = get_entity_name("ENTITY123")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/entity_names/ENTITY123")

        # Verify result
        self.assertIsInstance(result, EntityName)
        self.assertEqual(result.id, "ENTITY123")
        self.assertEqual(result.name, "Sample Entity")

    @patch("pagerduty_mcp.tools.entity_names.get_client")
    def test_create_entity(self, mock_get_client):
        """Test creating an entity."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.return_value = {"entity_name": self.sample_entity_response}

        # Create entity request instance
        entity_data = EntityNameCreate(name="New Entity", description="New entity description")
        entity_create = EntityNameCreateRequest(entity_name=entity_data)

        result = create_entity_name(entity_create)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once_with("/entity_names", json=entity_create.model_dump())

        # Verify result
        self.assertIsInstance(result, EntityName)
        self.assertEqual(result.id, "ENTITY123")
```

### 4.2 Competency Test Template

Competency tests verify that LLMs can correctly use the tools:

```python
# Example based on test_incidents.py and test_teams.py
class EntityNameCompetencyTest(CompetencyTest):
    """Tests that LLMs can correctly use entity name tools."""
    
    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register mock responses for entity name tools."""
        sample_entity = {
            "id": "ENTITY123",
            "name": "Sample Entity",
            "description": "Sample entity description",
        }
        
        sample_entities = [
            sample_entity,
            {
                "id": "ENTITY456",
                "name": "Another Entity",
                "description": "Another entity description",
            },
        ]
        
        # Register mock for list operation
        mcp.register_tool_response(
            "list_entity_names",
            {"response": [EntityName(**entity) for entity in sample_entities]},
            {"query_model": {"query": "Sample", "limit": 10}},
        )
        
        # Register mock for get operation
        mcp.register_tool_response(
            "get_entity_name", 
            EntityName(**sample_entity),
            {"entity_id": "ENTITY123"},
        )

# Define specific test cases
ENTITY_NAME_COMPETENCY_TESTS = [
    EntityNameCompetencyTest(
        query="Show me all sample entities",
        expected_tools=[
            {
                "tool_name": "list_entity_names",
                "parameters": {"query_model": {"query": "Sample"}},
            }
        ],
        description="Test fetching entities with a name filter",
    ),
    EntityNameCompetencyTest(
        query="Get details about entity ENTITY123",
        expected_tools=[
            {
                "tool_name": "get_entity_name",
                "parameters": {"entity_id": "ENTITY123"},
            }
        ],
        description="Test fetching a specific entity by ID",
    ),
]
```

## 5. Integration Guidelines

To integrate new tools with the PagerDuty MCP Server, follow these steps:

### 5.1 Tool Registration

All tools must be registered in the `tools/__init__.py` file:

```python
# Add imports for new tools
from .entity_names import (
    list_entity_names,
    get_entity_name,
    create_entity_name,
    update_entity_name,
    delete_entity_name,
)

# Add to read_tools for read-only operations
read_tools = [
    # Existing tools...
    # Add your read-only tools:
    list_entity_names,
    get_entity_name,
]

# Add to write_tools for operations that modify state
write_tools = [
    # Existing tools...
    # Add your write tools:
    create_entity_name,
    update_entity_name,
    delete_entity_name,
]
```

### 5.2 Tool Annotations

The `server.py` file automatically applies appropriate annotations:

- Read tools are marked as `readOnlyHint=True`, `destructiveHint=False`, `idempotentHint=True`
- Write tools are marked as `readOnlyHint=False`, `destructiveHint=True`, `idempotentHint=False`

These annotations help MCP clients understand the safety of each tool.

### 5.3 Error Handling

When implementing tools, follow these error handling practices:

1. Use explicit validation in models where possible
2. Allow exceptions to propagate up to the MCP framework
3. Return typed, structured responses that match the expected response models
4. Handle different API response formats (wrapped vs. direct)

## 6. Documentation Standards

Documentation for models and tools should follow these standards:

### 6.1 Model Field Documentation

```python
class EntityName(BaseModel):
    id: str | None = Field(
        description="The unique identifier of the entity",
        default=None,
    )
    name: str = Field(
        description="The human-readable name of the entity",
    )
```

### 6.2 Function Documentation

```python
def list_entity_names(query_model: EntityNameQuery) -> ListResponseModel[EntityName]:
    """List entity names matching the query parameters.
    
    Args:
        query_model: The model containing the query parameters
        
    Returns:
        ListResponseModel containing matching entities
    """
    # Implementation
```

### 6.3 Testing Documentation

```python
def test_list_entity_names_with_filters(self, mock_get_client, mock_paginate):
    """Test that entity listing works with various filters.
    
    Verifies:
    1. Correct parameters are passed to the paginate function
    2. Results are properly transformed to model instances
    3. Filtering behavior works as expected
    """
    # Test implementation
```

## 7. Implementation Checklist

When adding a new entity type to the PagerDuty MCP Server, follow this checklist:

1. **Models**:
   - [ ] Create entity model (`EntityName`)
   - [ ] Create query model (`EntityNameQuery`) with `to_params()` method
   - [ ] Create create/update models (`EntityNameCreate`, `EntityNameCreateRequest`)
   - [ ] Create reference model if needed (`EntityNameReference`)

2. **Tools**:
   - [ ] Implement list operation (`list_entity_names`)
   - [ ] Implement get operation (`get_entity_name`)
   - [ ] Implement create operation (`create_entity_name`)
   - [ ] Implement update operation (`update_entity_name`)
   - [ ] Implement delete operation (`delete_entity_name`)
   - [ ] Register tools in `tools/__init__.py`

3. **Tests**:
   - [ ] Create unit tests for all models and tools
   - [ ] Create competency tests for LLM tool usage

4. **Documentation**:
   - [ ] Add descriptive docstrings to all models and functions
   - [ ] Document model fields with clear descriptions
   - [ ] Update the README.md to include new tools in the tool table

## 8. Real-World Examples

### 8.1 List Operation (Read)

```python
# From pagerduty_mcp/tools/teams.py
def list_teams(query_model: TeamQuery) -> ListResponseModel[Team]:
    """List teams based on the provided query model.

    Args:
        query_model: The model containing the query parameters
    Returns:
        List of teams.
    """
    if query_model.scope == "my":
        # get my team references from /users/me
        user_data = get_user_data()
        user_team_ids = [team.id for team in user_data.teams]
        # Now get all team resources. Paginate limits to 1000 results by default
        results = paginate(client=get_client(), entity="teams", params={})
        teams = [Team(**team) for team in results if team["id"] in user_team_ids]
    else:
        response = paginate(client=get_client(), entity="teams", params=query_model.to_params())
        teams = [Team(**team) for team in response]
    return ListResponseModel[Team](response=teams)
```

### 8.2 Create Operation (Write)

```python
# From pagerduty_mcp/tools/services.py
def create_service(service_data: ServiceCreate) -> Service:
    """Create a new service.

    Args:
        service_data: The data for the new service.
        Do not include the ID in the data since it is auto-generated.
        Always include the summary field for all references if available.

    Returns:
        The created service
    """
    response = get_client().rpost("/services", json=service_data.model_dump())

    if type(response) is dict and "service" in response:
        return Service.model_validate(response["service"])

    return Service.model_validate(response)
```