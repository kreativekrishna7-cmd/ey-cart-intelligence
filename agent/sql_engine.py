import re

from sqlalchemy import text

from analytics.database import engine


ALLOWED_TABLES = {
    "customers",
    "products",
    "orders",
    "marketing_campaigns",
    "inventory",
    "returns",
}


FORBIDDEN_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "grant",
    "revoke",
    "merge",
    "replace",
}


def validate_sql(sql: str) -> tuple[bool, str]:

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    cleaned = sql.strip().rstrip(";")

    if not re.match(
        r"^(select|with)\b",
        cleaned,
        re.IGNORECASE,
    ):
        return False, "Only SELECT queries are allowed."

    normalized = re.sub(
        r"--.*?$|/\*.*?\*/",
        " ",
        cleaned,
        flags=re.MULTILINE | re.DOTALL,
    ).lower()

    for keyword in FORBIDDEN_KEYWORDS:

        if re.search(
            rf"\b{keyword}\b",
            normalized,
        ):
            return False, (
                f"Forbidden SQL operation detected: {keyword}"
            )

    table_matches = re.findall(
        r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        normalized,
    )

    unknown_tables = {
        table
        for table in table_matches
        if table not in ALLOWED_TABLES
    }

    if unknown_tables:
        return False, (
            "Query references tables that are not allowed: "
            + ", ".join(sorted(unknown_tables))
        )

    if ";" in cleaned:
        return False, "Multiple SQL statements are not allowed."

    return True, "SQL validation successful."


def execute_readonly_query(sql: str) -> list[dict]:

    valid, message = validate_sql(sql)

    if not valid:
        raise ValueError(message)

    with engine.connect() as connection:

        result = connection.execute(
            text(sql)
        )

        return [
            dict(row._mapping)
            for row in result
        ]
