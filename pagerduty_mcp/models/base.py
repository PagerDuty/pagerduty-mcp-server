from typing import Literal, TypeVar

from pydantic import BaseModel, computed_field

RequestScope = Literal["all", "my"]

DEFAULT_PAGINATION_LIMIT = 20
MAXIMUM_PAGINATION_LIMIT = 100
MAX_RESULTS = 1000

T = TypeVar("T", bound=BaseModel)


class ListResponseModel[T: BaseModel](BaseModel):
    """List response model.

    This model is used to wrap the responses from a list request
    so we can include additional metadata to help the agent interpret the response.
    It is generic so it can be used with any entity type (e.g., Incident, User, etc.).
    """

    response: list[T]

    @computed_field
    @property
    def response_summary(self) -> str:
        """Generate a summary of the response."""
        count = len(self.response)
        # Always resolve from generic type parameter when available
        generic_meta = getattr(type(self), "__pydantic_generic_metadata__", None)
        if generic_meta and generic_meta.get("args"):
            entity_type = generic_meta["args"][0].__name__
        elif self.response:
            entity_type = self.response[0].__class__.__name__
        else:
            entity_type = "Unknown"
        summary = [
            f"ListResponseModel<{entity_type}>:",
            f"- Returned {count} record(s) of type '{entity_type}'.",
        ]
        if count == MAX_RESULTS:
            summary.append(
                "- WARNING: The number of records equals the response limit. There may be more"
                " records not included in this response."
            )
        return "\n".join(summary)
