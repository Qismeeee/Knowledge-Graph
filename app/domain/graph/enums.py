from enum import StrEnum


class NodeLabel(StrEnum):
    ORG = "Org"
    REPO = "Repo"
    WORKSPACE = "Workspace"
    SERVICE = "Service"
    PACKAGE = "Package"
    FILE = "File"
    SYMBOL = "Symbol"
    ENDPOINT = "Endpoint"
    TOPIC = "Topic"
    DB_TABLE = "DBTable"
    DEPENDENCY = "Dependency"
    DOC_NODE = "DocNode"
    INDEX_RUN = "IndexRun"


class RelationType(StrEnum):
    CONTAINS = "CONTAINS"
    DECLARES = "DECLARES"
    CONTAINS_SYMBOL = "CONTAINS_SYMBOL"
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    INHERITS = "INHERITS"
    IMPLEMENTS = "IMPLEMENTS"
    USES_DEPENDENCY = "USES_DEPENDENCY"
    EXPOSES = "EXPOSES"
    HANDLED_BY = "HANDLED_BY"
    CALLS_ENDPOINT = "CALLS_ENDPOINT"
    READS_TABLE = "READS_TABLE"
    WRITES_TABLE = "WRITES_TABLE"
    PUBLISHES = "PUBLISHES"
    SUBSCRIBES = "SUBSCRIBES"
    DEPENDS_ON = "DEPENDS_ON"
    DOCUMENTED_BY = "DOCUMENTED_BY"
