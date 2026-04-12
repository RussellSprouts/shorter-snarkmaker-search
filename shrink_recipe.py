from optimized_stream_simulation import optimized_stream_simulation
import sys
import sqlite3
from collections import defaultdict

print(sum((0, 135, 93, 105, 107, 115, 91, 105, 102, 118, 101, 96, 92, 138, 151, 147, 129, 108, 91, 116, 154, 149, 128, 114, 202, 128, 128, 120, 110, 113, 162, 115, 90, 91, 146, 127, 103, 118, 135, 176, 124, 180, 96, 108, 210, 91, 90, 111, 111, 99, 104, 202, 174, 135, 111, 214, 116, 94, 182, 91, 93, 190, 103, 106, 95, 96, 117, 91, 122, 110, 147, 117, 91, 120, 92, 105, 149, 108, 119, 102, 106, 126, 124, 106, 128, 150, 130, 132, 134, 90, 197, 99, 132, 91, 161, 146, 100, 108, 145, 97, 138, 100, 101, 167, 91, 183, 140, 90, 94, 99, 93, 100, 105, 102, 153, 105, 92, 121, 92, 90, 99, 96, 97, 116, 91, 193, 94, 91, 117, 100, 103, 122, 121, 90, 109, 205, 90, 105, 110, 93, 232, 108, 100, 93, 145, 118, 106, 90, 101, 151, 134, 113, 141, 96, 91, 123, 91, 111, 90, 102, 95, 105, 93)))
print(sum((0, 135, 93, 105, 107, 115, 91, 105, 102, 118, 101, 96, 92, 138, 151, 147, 129, 108, 91, 116, 154, 149, 128, 114, 202, 128, 128, 120, 110, 113, 162, 115, 90, 91, 146, 127, 103, 118, 135, 176, 124, 180, 96, 108, 218, 91, 90, 111, 111, 99, 104, 202, 174, 135, 111, 214, 116, 94, 182, 91, 93, 190, 103, 106, 95, 96, 117, 91, 122, 110, 147, 117, 91, 120, 92, 105, 149, 108, 119, 102, 106, 126, 124, 106, 128, 150, 130, 132, 134, 90, 197, 99, 132, 91, 161, 146, 100, 108, 145, 97, 138, 100, 101, 167, 91, 183, 140, 90, 94, 99, 93, 100, 105, 102, 153, 105, 92, 121, 92, 90, 99, 96, 97, 116, 91, 193, 94, 91, 117, 100, 103, 122, 121, 90, 109, 205, 90, 105, 110, 93, 232, 108, 100, 93, 145, 118, 106, 90, 101, 151, 134, 113, 141, 96, 91, 123, 91, 111, 90, 102, 95, 198)))

sys.exit(1)

if __name__ == "__main__":
    databases = sys.argv[1:]
    before_hit_digests = []
    recipe = (0, 135, 93, 105, 107, 115, 91, 105, 102, 118, 101, 96, 92, 138, 151, 147, 129, 108, 91, 116, 154, 149, 128, 114, 202, 128, 128, 120, 110, 113, 162, 115, 90, 91, 146, 127, 103, 118, 135, 176, 124, 180, 96, 108, 210, 91, 90,111,111,99,104,202,174,135,111,214,116,94,182,91,93,190,103,106,95,96,117,91,122,110,147,117,91,120,92,105,149,108,119,102,106,126,124,106,128,150,130,132,134,90,197,99,132,91,161,146,100,108,145,97,138,100,101,167,91,183,140,90,94,99,93,100,105,102,153,105,92,121,92,90,99,96,97,116,91,193,94,91,117,100,103,122,121,90,109,205,90,105,110,93,232,108,100,93,145,118,106,90,101,151,134,113,141,96,91,123,91,111,90,102,95,198,107,122,162,90,114,96,92,114,127,109,126,98,135,95,141,114,98,124,102,148,129,91,92,136,107,249,181,93,141,106,109,98,113,95,128,108,250,105,98,109,100,96,170,94,95,102,101,206,98,100,170,111,152,169,97,141,186,100,101,94,96,95,110,95,134,111,98,115,91,91,96,102,98,98,101,175,156,238,100,99,172,116,122,212,146,96,138,152,101,104,96,98,131,138,127,103,94,129,96,120,147,98,142,128)
    results_by_digest=defaultdict(list)
    for i in range(1, len(recipe)):
        sub_recipe = recipe[0:i]
        patt = optimized_stream_simulation(sub_recipe)
        # patt = patt("swap_xy", 1, 0) # our results use flipped_offset_block
        before_hit_digest = patt.digest()
        print(i, before_hit_digest)
        before_hit_digests.append(str(before_hit_digest))
        results_by_digest[before_hit_digest].append({
            'input': 'original',
            'stream': bytes(sub_recipe),
        })

    for filename in databases:
        try:
            print(filename)
            conn = sqlite3.connect(filename)
            results = conn.execute(f"""
                select starting_points.stream, results.stream, before_hit_digest
                from results
                join starting_points
                on results.starting_point = starting_points.id
                where before_hit_digest in ({','.join(before_hit_digests)})
            """)

            for (s1, s2, d) in results:
                results_by_digest[d].append({
                    'input': filename,
                    'stream': s1 + s2
                })
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("failed, moving on")
            print(e)

    for k, v in results_by_digest.items():
        first = v[0]
        first_cost = (len(first['stream']), sum(first['stream']))
        rest = v[1:]
        for r in rest:
            other_cost = (len(r['stream']), sum(r['stream']))

            if other_cost < first_cost:
                print("digest", k)
                print("found a better cost!", first_cost, other_cost)
                print("found in", r['input'])
                print("was ", tuple(first['stream']))
                print("better", tuple(r['stream']))
