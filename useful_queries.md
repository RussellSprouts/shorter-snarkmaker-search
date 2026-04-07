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