"""
JSON Schema definitions for Urban Scooter courier API responses.
Used with jsonschema.validate() in tests to catch contract breaks
even when status codes look correct.
"""

CREATE_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["ok"],
    "properties": {
        "ok": {"type": "boolean"}
    },
    "additionalProperties": False
}

LOGIN_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["id"],
    "properties": {
        "id": {"type": "integer", "minimum": 1}
    }
}

DELETE_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["ok"],
    "properties": {
        "ok": {"type": "boolean"}
    },
    "additionalProperties": False
}

ERROR_SCHEMA = {
    "type": "object",
    "required": ["message"],
    "properties": {
        "message": {"type": "string"}
    }
}
