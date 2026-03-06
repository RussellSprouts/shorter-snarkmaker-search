# Useful SQL queries

## See the breakdown of full_intermediates in the results

Use `sqlite3 results.sqlite`.

```sql
SELECT full_intermediate, COUNT(full_intermediate), LENGTH(fi.so_far)/2 FROM results JOIN recipe_intermediates fi ON fi.id = full_intermediate GROUP BY full_intermediate;
```


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
) WHERE row_num = 0;
```

SELECT *, full_intermediate_overlapping_digest as label FROM (SELECT *, ROW_NUMBER() OVER ( PARTITION BY full_intermediate_overlapping_digest ORDER BY length(r.stream) + length(sp.stream)) as row_num FROM results r JOIN starting_points sp ON sp.id = starting_point JOIN recipe_intermediates fi ON fi.id = full_intermediate WHERE depth <= 0 and length(fi.so_far) >= 26) WHERE row_num = 1 ORDER BY full_intermediate_overlapping_population LIMIT 10;