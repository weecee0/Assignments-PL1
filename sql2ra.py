def parse_sql(sql_query):
    """
    Manually parse the SQL query to extract SELECT, FROM, WHERE, and JOIN clauses.
    Also handles set operations like UNION, INTERSECT, and EXCEPT.
    """
    sql_query = sql_query.strip().lower()

    # Check for set operations (UNION, INTERSECT, EXCEPT)
    set_operation = ""
    if "union" in sql_query:
        sql_query, remainder = sql_query.split("union", 1)
        set_operation = "∪"
    elif "intersect" in sql_query:
        sql_query, remainder = sql_query.split("intersect", 1)
        set_operation = "∩"
    elif "except" in sql_query:
        sql_query, remainder = sql_query.split("except", 1)
        set_operation = "-"

    # Extract SELECT clause
    select_start = sql_query.find("select") + len("select")
    from_start = sql_query.find("from")
    select_clause = sql_query[select_start:from_start].strip()

    # Extract FROM and JOIN clauses
    where_start = sql_query.find("where")
    if where_start != -1:
        from_clause = sql_query[from_start + len("from"):where_start].strip()
        where_clause = sql_query[where_start + len("where"):].strip()
    else:
        from_clause = sql_query[from_start + len("from"):].strip()
        where_clause = ""

    return select_clause, from_clause, where_clause, set_operation, remainder if set_operation else None


def translate_join(from_clause):
    """
    Translates FROM and JOIN clauses to relational algebra.
    Handles natural joins if present.
    """
    # Check if there is a JOIN in the FROM clause
    if "join" in from_clause:
        tables = []
        conditions = []
        
        # Extract tables and join conditions
        parts = from_clause.split("join")
        base_table = parts[0].strip()
        tables.append(base_table)
        
        for part in parts[1:]:
            table, condition = part.split("on")
            tables.append(table.strip())
            conditions.append(condition.strip())
        
        # Create relational algebra for join
        join_conditions = " ∧ ".join(conditions)
        join_expression = f"({tables[0]} ⨝ {tables[1]} ON {join_conditions})"
        
        return join_expression
    else:
        return from_clause.strip()


def translate_to_relational_algebra(select_clause, from_clause, where_clause, set_operation="", remainder=None):
    """
    Translate SQL clauses to relational algebra expressions, including joins and set operations.
    """
    # Handle SELECT clause -> Projection (π)
    select_columns = [col.strip() for col in select_clause.split(",")]
    projection = f"π({', '.join(select_columns)})"
    
    # Handle WHERE clause -> Selection (σ)
    if where_clause:
        selection = f"σ({where_clause})"
    else:
        selection = ""
    
    # Handle FROM and JOIN clauses
    relation = translate_join(from_clause)
    
    # Combine Projection and Selection into the final relational algebra expression
    if selection:
        relational_algebra_expr = f"{projection}({selection}({relation}))"
    else:
        relational_algebra_expr = f"{projection}({relation})"
    
    # Handle set operations (UNION, INTERSECT, EXCEPT)
    if set_operation:
        # Parse the second query after set operation
        remainder_select, remainder_from, remainder_where, _, _ = parse_sql(remainder)
        second_expr = translate_to_relational_algebra(remainder_select, remainder_from, remainder_where)
        relational_algebra_expr = f"({relational_algebra_expr}) {set_operation} ({second_expr})"
    
    return relational_algebra_expr


# Example SQL query with JOIN and UNION
sql_query2 = """
SELECT employees.name, departments.name
FROM employees
JOIN departments ON employees.dept_id = departments.id
WHERE employees.age > 30
UNION
SELECT employees.name, departments.name
FROM employees
JOIN departments ON employees.dept_id = departments.id
WHERE employees.age < 25
"""

sql_query = """
SELECT employees.name, departments.name
FROM employees
JOIN departments ON employees.dept_id = departments.id
WHERE employees.age > 30
"""

# Step 1: Parse the SQL query
select_clause, from_clause, where_clause, set_operation, remainder = parse_sql(sql_query)

# Step 2: Translate to relational algebra
relational_algebra_expr = translate_to_relational_algebra(select_clause, from_clause, where_clause, set_operation, remainder)

# Output the result
print("RA Expression:", relational_algebra_expr)

