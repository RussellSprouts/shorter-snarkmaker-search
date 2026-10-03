# Useful SQL queries

## See the breakdown of full_intermediates in the results

```sql
SELECT full_intermediate, COUNT(distinct before_hit_digest) as count, LENGTH(fi_so_far)/2 as progress, MAX(full_intermediate_depth_separation), MIN(depth) FROM r GROUP BY full_intermediate ORDER BY progress desc, count desc;
```

## See the unique patterns of the zero degree elbow which overlap the depth range of the full_intermediate

```sql
SELECT * FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY full_intermediate_overlapping_digest
            ORDER BY length(r.stream) + length(sp.stream)
        ) as row_num
    FROM results r
    JOIN starting_points sp ON sp.id = starting_point
    JOIN recipe_intermediates fi ON fi.id = full_intermediate
    WHERE depth <= 0 and length(fi.so_far) >= 26
) WHERE row_num = 1;
```

SELECT *, full_intermediate_overlapping_digest as label FROM (SELECT *, ROW_NUMBER() OVER ( PARTITION BY full_intermediate_overlapping_digest ORDER BY length(fi.so_far) desc, length(r.stream) + length(sp.stream)) as row_num FROM results r JOIN starting_points sp ON sp.id = starting_point JOIN recipe_intermediates fi ON fi.id = full_intermediate WHERE depth <= 0 and length(fi.so_far) >= 28) WHERE row_num = 1 ORDER BY full_intermediate_depth_separation desc LIMIT 20;

SELECT *, cast(full_intermediate_overlapping_digest as text) || " " || cast(full_intermediate_overlapping_population as text) as label FROM (SELECT *, ROW_NUMBER() OVER ( PARTITION BY full_intermediate_overlapping_digest ORDER BY length(fi.so_far) desc, length(r.stream) + length(sp.stream)) as row_num FROM results r JOIN starting_points sp ON sp.id = starting_point JOIN recipe_intermediates fi ON fi.id = full_intermediate WHERE depth <= 40 and length(fi.so_far)/2 = 73) WHERE row_num = 1 ORDER BY full_intermediate_overlapping_population LIMIT 100;

## See the unique partial intermediates

SELECT *, partial_intermediate as label FROM (SELECT *, ROW_NUMBER() OVER ( PARTITION BY partial_intermediate order by partial_intermediate_positive_log_prob) as row_num FROM r ORDER BY partial_intermediate_log_prob DESC) WHERE row_num = 1 ORDER BY length(pi_so_far) desc;


## Find the total cost

```
WITH RECURSIVE unpack_hex AS (
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
        (INSTR('0123456789ABCDEF', SUBSTR(hex_pair, 1, 1)) - 1) * 16 +
        (INSTR('0123456789ABCDEF', SUBSTR(hex_pair, 2, 1)) - 1) AS decimal_val
    FROM unpack_hex
    WHERE hex_pair != ''
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
LIMIT 10;
```