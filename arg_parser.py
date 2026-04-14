import re

def range_str_to_list(r):
    tokens = re.split(r'([-,])', r)
    tokens = list(filter(lambda a: a ,map(lambda a: a.strip(), tokens)))
    
    def parse_number():
        if not tokens:
            raise ValueError("Expected a number, but was empty")
        if tokens[0] == '-':
            # negative number
            return int(tokens.pop(0) + tokens.pop(0))
        return int(tokens.pop(0))

    def parse_item():
        if not tokens:
            raise ValueError("Expected a value for range item, but got nothing")
        if tokens[0] != '-' and not re.match('[0-9]', tokens[0]):
            raise ValueError(f"Expected a number for range item, but got {repr(tokens[0])}")
        start = parse_number()
        end = start
        if tokens and tokens[0] == '-':
            # range
            tokens.pop(0)
            end = parse_number()

        return list(range(start, end+1))

    def parse_comma_separated():
        items = [*parse_item()]
        while tokens and tokens[0] == ',':
            tokens.pop(0)
            items += parse_item()
        return items

    result = parse_comma_separated()
    result.sort()
    return result