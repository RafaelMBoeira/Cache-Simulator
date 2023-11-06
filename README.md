## Informações:

Este trabalho é uma implementação em Python de um simulador de memórias cache com diferentes políticas de substituição (Random, FIFO, LRU).

## Execução do programa:

O programa pode ser executado a partir da seguinte linha de comando:

python cache_simulator.py <nsets> <bsize> <assoc> <pol> <output_flag> <input_file>

onde:
    - nsets: número de conjutos da cache
    - bsize: tamanho do bloco
    - assoc: associatividade
    - pol: política de substituição
    - output_flag: flag que define formato da saída
    - input_file: arquivo '.bin' com as requisições de endereço
