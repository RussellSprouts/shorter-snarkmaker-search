
def range_str_to_list(r):
    result = []
    for s in r.split(','):
        if '-' in s:
            start, end = s.split('-')
            result += list(range(int(start), int(end)+1))
        else:
            result.append(int(s))
    result.sort()
    return result
