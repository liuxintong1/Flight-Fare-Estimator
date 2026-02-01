class MyTable:
    def __init__(self, columns, rows):
        self.columns = columns            # ["name", "age", "city"]
        self.rows = rows                  # list of dicts

    #parse data
    #default delimiter is ","
    @classmethod
    def from_file(cls,path, delimiter=","):
        lines = []
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    lines.append(line.strip())
        
        # First line: headers
        columns = []
        for c in lines[0].split(delimiter):
            columns.append(c.strip())
        
        # Remaining lines: data rows
        rows = []
        for i, line in enumerate(lines[1:], start=2):
            values = [v.strip() for v in split_csv_line(line, delimiter)]
    
            # Adjust number of values to match columns
            if len(values) < len(columns):
                # Fill missing columns with empty strings
                values += [""] * (len(columns) - len(values))
            elif len(values) > len(columns):
                # Truncate extra values (warn but keep the row)
                print(f" Line {i} has {len(values)} values (expected {len(columns)}). Truncating extras.")
                values = values[:len(columns)]
    
            row = dict(zip(columns, values))
    
            # Convert numeric values where possible
            for k, v in row.items():
                if isinstance(v, str) and v.strip() == "":
                    # Keep empty strings as-is (for later cleaning)
                    continue
                elif v.isdigit():
                    row[k] = int(v)
                else:
                    try:
                        row[k] = float(v)
                    except ValueError:
                        pass
    
            rows.append(row)
        return cls(columns, rows)

    def filter(self, condition_fn):
        filtered = []
        for row in self.rows:
            result = condition_fn(row)
            if result:
                filtered.append(row)
        
        return MyTable(self.columns, filtered)

    def select(self, columns):
        """
        Return a new MyTable containing only the specified columns.
        `columns` can be a list of names (label-based) or indices (integer-based).
        """
        # If selecting by indices
        if all(isinstance(c, int) for c in columns):
            selected_columns = [self.columns[i] for i in columns]
        else:
            selected_columns = columns

        new_rows = []
        for row in self.rows:
            # only keep the selected keys
            new_row = {col: row.get(col, "") for col in selected_columns}
            new_rows.append(new_row)

        return MyTable(selected_columns, new_rows)


    def head(self, n=5):
        for row in self.rows[:n]:
            print(row)
    
    def drop_missing(self, columns=None):
        """
        Remove rows with missing values.
        If `columns` is None, check all columns.
        Otherwise, only check the specified columns.
        """
        cleaned_rows = []
        missing_indicators = {"", None, "NA", "N/A", "null", "NaN"}
    
        for row in self.rows:
            # Choose which columns to check
            cols_to_check = columns or self.columns
    
            # Check if any column has a missing value
            has_missing = any(
                (row.get(col) in missing_indicators)
                for col in cols_to_check
            )
    
            # Keep the row only if it's fully valid
            if not has_missing:
                cleaned_rows.append(row)
    
        return MyTable(self.columns, cleaned_rows)
    
    def groupby(self, by):
        """Group rows by one or more columns and return a GroupBy object."""
        if isinstance(by, str):
            by = [by]

        groups = {}
        for row in self.rows:
            key = tuple(row[col] for col in by)
            if len(by) == 1:
                key = key[0]
            groups.setdefault(key, []).append(row)

        return GroupBy(groups, by)

    def join(self, other, on, how="inner"):
        """
        Join this table with another MyTable.
        
        Args:
            other (MyTable): The other table to join with.
            on (str | list): Column(s) to join on.
            how (str): Join type: 'inner', 'left', 'right', 'outer'
        """
        if isinstance(on, str):
            on = [on]

        # Index other table by join key
        other_index = {}
        for row in other.rows:
            key = tuple(row[col] for col in on)
            other_index.setdefault(key, []).append(row)

        joined_rows = []
        self_keys_seen = set()
        other_keys_seen = set()

        for row in self.rows:
            key = tuple(row[col] for col in on)
            self_keys_seen.add(key)

            if key in other_index:
                # Matching rows found → combine all
                for other_row in other_index[key]:
                    combined = {**row, **other_row}
                    joined_rows.append(combined)
                other_keys_seen.add(key)
            elif how in ("left", "outer"):
                # Left/Outer join keeps left row even if no match
                combined = {**row}
                for col in other.columns:
                    if col not in combined:
                        combined[col] = None
                joined_rows.append(combined)

        # Handle right/outer join for rows in 'other' not matched
        if how in ("right", "outer"):
            for row in other.rows:
                key = tuple(row[col] for col in on)
                if key not in self_keys_seen:
                    combined = {**row}
                    for col in self.columns:
                        if col not in combined:
                            combined[col] = None
                    joined_rows.append(combined)

        # Resolve final columns (combine and deduplicate)
        all_columns = list(dict.fromkeys(self.columns + other.columns))
        return MyTable(all_columns, joined_rows)


class GroupBy:
    def __init__(self, groups, columns):
        self.groups = groups  # dict: key -> list of rows
        self.columns = columns

    def agg(self, agg_map):
        """
        Perform aggregation on grouped data.
        Example: {"price": "mean"} or {"price": "median"}
        """
        results = []

        for key, rows in self.groups.items():
            result_row = {}

            # handle group keys (single or multiple)
            if isinstance(key, tuple):
                for i, k in enumerate(key):
                    result_row[self.columns[i]] = k
            else:
                result_row[self.columns[0]] = key

            # perform aggregation per column
            for col, func in agg_map.items():
                values = [r[col] for r in rows if isinstance(r[col], (int, float))]

                if not values:
                    result = None
                elif func == "sum":
                    result = sum(values)
                elif func == "mean":
                    result = sum(values) / len(values)
                elif func == "count":
                    result = len(values)
                elif func == "min":
                    result = min(values)
                elif func == "max":
                    result = max(values)
                elif func == "median":
                    sorted_vals = sorted(values)
                    n = len(sorted_vals)
                    mid = n // 2
                    if n % 2 == 0:
                        result = (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
                    else:
                        result = sorted_vals[mid]
                else:
                    raise ValueError(f"Unknown aggregation: {func}")

                result_row[col + "_" + func] = result

            results.append(result_row)

        new_columns = list(results[0].keys()) if results else []
        return MyTable(new_columns, results)


# helper method to avoid separating location: eg. "Seattle,WA" to "Seattle" "WA"
def split_csv_line(line, delimiter=","):
    values = []
    current = ""
    inside_quotes = False

    for char in line:
        if char == '"':
            inside_quotes = not inside_quotes
        elif char == delimiter and not inside_quotes:
            values.append(current.strip())
            current = ""
        else:
            current += char
    values.append(current.strip())

    # Remove surrounding quotes if any
    values = [v[1:-1] if v.startswith('"') and v.endswith('"') else v for v in values]
    return values


    