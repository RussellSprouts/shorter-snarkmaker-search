```
uv run snark.py setup-next-search -i results/blinker-elbow/1.sqlite -o results/blinker-elbow/2.sqlite -q 'WITH RECURSIVE unpack_hex AS (
    -- Anchor member: Grab every row and extract the first 2 hex characters
    SELECT 
        orig_rowid,
        HEX(full_stream) AS hex_string,
        1 AS pos,
        SUBSTR(HEX(full_stream), 1, 2) AS hex_pair
    FROM r
    
    UNION ALL
    
    -- Recursive member: Advance by 2 hex characters row-by-row
    SELECT 
        orig_rowid,
        hex_string,
        pos + 2,
        SUBSTR(hex_string, pos + 2, 2)
    FROM unpack_hex
    WHERE pos + 2 <= LENGTH(hex_string)
),
byte_values AS (
    -- Map each hex pair back to its 0-255 decimal value
    SELECT 
        orig_rowid,
        (INSTR("0123456789ABCDEF", SUBSTR(hex_pair, 1, 1)) - 1) * 16 +
        (INSTR("0123456789ABCDEF", SUBSTR(hex_pair, 2, 1)) - 1) AS decimal_val
    FROM unpack_hex
    WHERE hex_pair != ""
),
summed_bytes AS (
    -- Aggregate the sums grouped by the original row orig_rowid
    SELECT 
        orig_rowid, 
        SUM(decimal_val) AS total_byte_sum
    FROM byte_values
    GROUP BY orig_rowid
)
-- Final step: Join the sums back to your original table to append the column
SELECT 
    r.*,
    COALESCE(s.total_byte_sum, 0) AS total_gens,
    CAST(far_depth as float) / (90 + COALESCE(s.total_byte_sum, 0)) as label
FROM r
LEFT JOIN summed_bytes s ON r.orig_rowid = s.orig_rowid
WHERE far_depth < 30
ORDER BY label
LIMIT 1000' -q 'WITH RECURSIVE unpack_hex AS (
    -- Anchor member: Grab every row and extract the first 2 hex characters
    SELECT 
        orig_rowid,
        HEX(full_stream) AS hex_string,
        1 AS pos,
        SUBSTR(HEX(full_stream), 1, 2) AS hex_pair
    FROM r
    
    UNION ALL
    
    -- Recursive member: Advance by 2 hex characters row-by-row
    SELECT 
        orig_rowid,
        hex_string,
        pos + 2,
        SUBSTR(hex_string, pos + 2, 2)
    FROM unpack_hex
    WHERE pos + 2 <= LENGTH(hex_string)
),
byte_values AS (
    -- Map each hex pair back to its 0-255 decimal value
    SELECT 
        orig_rowid,
        (INSTR("0123456789ABCDEF", SUBSTR(hex_pair, 1, 1)) - 1) * 16 +
        (INSTR("0123456789ABCDEF", SUBSTR(hex_pair, 2, 1)) - 1) AS decimal_val
    FROM unpack_hex
    WHERE hex_pair != ""
),
summed_bytes AS (
    -- Aggregate the sums grouped by the original row orig_rowid
    SELECT 
        orig_rowid, 
        SUM(decimal_val) AS total_byte_sum
    FROM byte_values
    GROUP BY orig_rowid
)
-- Final step: Join the sums back to your original table to append the column
SELECT 
    r.*,
    COALESCE(s.total_byte_sum, 0) AS total_gens,
    CAST(depth as float) / (90 + COALESCE(s.total_byte_sum, 0)) as label
FROM r
LEFT JOIN summed_bytes s ON r.orig_rowid = s.orig_rowid
WHERE depth < 30
ORDER BY label
LIMIT 1000' -q 'select * from r order by depth limit 1000' -q 'select * from r order by far_depth limit 1000'
```