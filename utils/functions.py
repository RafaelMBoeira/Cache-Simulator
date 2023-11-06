import struct
import sys
import math

def parse_input() -> dict():
    """
        Coloca em um dicionário os parâmetros de inicialização do programa.
    """
    assert len(sys.argv) == 7 # Quantidade de argumentos inválida!
    return {'n_sets': int(sys.argv[1]), 'b_size': int(sys.argv[2]), 'assoc': int(sys.argv[3]), 'pol': sys.argv[4], 'flag': int(sys.argv[5]), 'filename': sys.argv[6]}

def read_file(file_dir: str) -> list[int]:
    """
        Lê um arquivo .bin.
    """
    try:
        with open(file_dir, 'rb') as file:
            bin_file = file.read()
    except:
        raise FileNotFoundError('Arquivo não encontrado')

    return bin_file

def convert_to_address(bin_file: bytes, word_size: int, n_sets: int, block_size: int) -> list[list[int]]:
    """
        Converte uma sequência de bytes em inteiros de 32 bits com
        formatação big endian através da biblioteca struct.\n
            '>' : big endian\n
            'I' : int32\n
        E extrai seu index e sua tag, retornando todas as requisições em formato [index, tag].
        
    """
    assert len(bin_file) % word_size == 0 # tamanho do arquivo precisa ser divisível pelo tamanho da palavra

    n_requests = int(len(bin_file) / word_size)
    addresses = []

    for m in range(n_requests):
        ini = m * word_size
        end = ini + word_size

        bin_word = bin_file[ini:end]               

        addr = struct.unpack('>I', bin_word)[0]     
        cache_dir = extract_cache_dir(addr, n_sets, block_size)
        
        addresses.append(cache_dir)

    return addresses

def extract_cache_dir(address: int, n_sets: int, block_size: int) -> tuple[int]:
    """
        Extrai a tag e o index dos endereços solicitados.
    """
    bits_index = int(math.log(n_sets, 2))
    bits_offset = int(math.log(block_size, 2))

    index = (address >> bits_offset) & ((2 ** bits_index) - 1)    
    tag = address >> (bits_offset + bits_index)

    return tuple([index, tag])

def print_output(hits: int, errors: dict, flag: int, n_reqs: int) -> None:
    """
        Função de visualização dos parâmetros de saída.
    """
    miss_counter = sum(errors.values())
    miss_rate = miss_counter/n_reqs

    if flag == 0:
        print(f'Requisições: {n_reqs} | Hit Rate: {hits/n_reqs:.4f} | Miss Rate: {miss_rate:.4f} |', end=' ')
    else:
        print(f'{n_reqs} {hits/n_reqs:.4f} {miss_rate:.4f}', end=' ')

    for error, quantity in errors.items():    
        if flag == 0:
            print(f'{error}: {quantity/miss_counter:.4f} |', end=' ')
        else:
            print(f'{quantity/miss_counter:.4f}', end=' ')
    print()
