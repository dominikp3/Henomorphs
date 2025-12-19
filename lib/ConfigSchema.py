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
        "ai_defender_delay": {"type": "number", "minimum": 0},
        "debug": {"type": "boolean"},
        "dummy": {"type": "integer", "minimum": 0, "maximum": 2},
        "rpc": {"type": "string"},
        "log": {"type": "boolean"},
        "print_tx_hash": {"type": "boolean"},
        "print_priv_key": {"type": "boolean"},
        "gas_mul": {"type": "number", "minimum": 0.5},
        "gas_max_total": {"type": "number"},
        "gas_max_priority": {"type": "number"},
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
        "terrain_maintenance_threshold": {
            "type": "integer",
            "minimum": 86400,
            "maximum": 259200,
        },
        "terrain_repair_threshold": {"type": "integer", "minimum": 0},
        "anti_betrayal": {"type": "boolean"},
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
            "TokenID": {"type": "integer", "minimum": 0},
            "Action": {"type": "integer", "minimum": 0, "maximum": 8},
            "Spec": {"type": "integer", "minimum": -1, "maximum": 2},
        },
    },
}

colony_config_schema = {
    "type": "object",
    "properties": {
        "Colony": {"type": "string", "pattern": "^0x[a-fA-F0-9]{64}$"},
        "Season": {"type": "integer", "minimum": 0},
        "WarKits": {
            "type": "array",
            "uniqueItems": True,
            "minItems": 1,
            "items": {
                "required": ["CollectionIDs", "TokenIDs"],
                "properties": {
                    "CollectionIDs": {
                        "type": "array",
                        "minItems": 2,
                        "items": {"type": "integer", "minimum": 2, "maximum": 3},
                    },
                    "TokenIDs": {
                        "type": "array",
                        "minItems": 2,
                        "items": {"type": "integer", "minimum": 0},
                    },
                    "name": {"type": "string"},
                },
            },
        },
    },
    "additionalProperties": False,
    "required": ["Colony", "WarKits", "Season"],
}
