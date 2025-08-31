config_schema = {
    "definitions": {
        "repair": {
            "type": "object",
            "properties": {
                "threshold": {"type": "integer", "minimum": -1},
                "max_repair": {"type": "integer", "minimum": -1},
            },
            "additionalProperties": False,
        },
        "algorithm": {
            "type": "string",
            "pattern": "(ask|sequence|batch)",
        },
    },
    "type": "object",
    "properties": {
        "max_transaction_attempts": {"type": "integer", "minimum": 1},
        "random_action_on_fail": {"type": "integer", "minimum": 0},
        "delay": {"type": "number", "minimum": 0},
        "debug": {"type": "boolean"},
        "dummy": {"type": "integer", "minimum": 0, "maximum": 2},
        "rpc": {"type": "string"},
        "log": {"type": "boolean"},
        "repair_wear": {"$ref": "#/definitions/repair"},
        "repair_charge": {"$ref": "#/definitions/repair"},
        "algorithms": {
            "type": "object",
            "properties": {
                "actions": {"$ref": "#/definitions/algorithm"},
                "repair_wear": {"$ref": "#/definitions/algorithm"},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

heno_config_schema = {
    "type": "array",
    "uniqueItems": True,
    "items": {
        "required": ["CollectionID", "TokenID", "Action"],
        "properties": {
            "CollectionID": {"type": "integer", "minimum": 2, "maximum": 3},
            "TokenID": {"type": "integer", "minimum": 2},
            "Action": {"type": "integer", "minimum": 0, "maximum": 8},
            "Spec": {"type": "integer", "minimum": -1, "maximum": 2},
        },
    },
}
