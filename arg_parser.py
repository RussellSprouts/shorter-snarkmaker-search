
def range_str_to_list(r):
    result = []
    for s in r.split(','):
        print(s)
        if '-' in s:
            start, end = s.split('-')
            result += list(range(int(start), int(end)+1))
        else:
            result.append(int(s))
    result.sort()
    return result

print(range_str_to_list('74,75,78-255'))