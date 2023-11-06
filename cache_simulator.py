from models.modules import CacheFactory
from utils.functions import parse_input, read_file, convert_to_address, print_output

WORD_SIZE = 4

if __name__ == '__main__':
    args = parse_input()
    
    factory = CacheFactory()
    cache = factory.create_cache(args['n_sets'], args['b_size'], args['assoc'], args['pol'])
    
    output_flag = args['flag']

    file = read_file(args['filename'])
    addresses = convert_to_address(file, WORD_SIZE, args['n_sets'], args['b_size'])
    
    n_reqs = len(addresses)
    for addr in addresses:
        index, tag = addr
        cache.request(index, tag)

    print_output(cache.hits, cache.errors, output_flag, n_reqs)