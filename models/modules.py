import math
import random
from abc import ABC, abstractmethod

class Cache(ABC):
    def __init__(self, n_sets: int, block_size: int, associativity: int, pol: str):
        self.n_sets = n_sets
        self.block_size = block_size
        self.associativity = associativity
        self.pol = pol.lower()
        self.errors = {'Compulsório': 0, 'Capacidade': 0, 'Conflito': 0}
        self.hits = 0

    def _hash_function(self, index: int) -> int:
        """
            Função de mapeamento do endereço para um conjunto da cache.
        """
        return index % self.n_sets
    
    @abstractmethod
    def request(self, index: int, tag: int) -> bool:
        """
            Função que recebe o index e tag do endereço solicitado e o procura 
            na cache.
        """
        pass

    @abstractmethod
    def _fault_treatment(self, set_destiny: int, tag: int) -> None:
        """
            Função que trata a falta de um endereço na cache através de diferentes
            algoritmos de substituição:\n
                'r': Random\n
                'f': FIFO\n
                'l': LRU\n

            Mapeamento direto não utiliza nenhum deles.
        """
        pass
    
class DirectMappingCache(Cache):
    def __init__(self, n_sets: int, block_size: int, associativity: int, pol: str):
        super().__init__(n_sets, block_size, associativity, pol)

        self._validation_bits = [0 for _ in range(n_sets)]
        self._tags = [0 for _ in range(n_sets)]

    def request(self, index: int, tag: int) -> bool:
        set_destiny = self._hash_function(index)

        if self._validation_bits[set_destiny] == 0:
            self._fault_treatment(set_destiny, tag)
            self.errors['Compulsório'] += 1
            return False            
        else:
            current_tag = self._tags[set_destiny]

            if current_tag == tag:
                self.hits += 1
                return True
    
        self._fault_treatment(set_destiny, tag)
        self.errors['Conflito'] += 1
        return False 

    def _fault_treatment(self, set_destiny: int, tag: int) -> None:
        self._validation_bits[set_destiny] = 1
        self._tags[set_destiny] = tag
    
class AssociativeMappingCache(Cache):
    def __init__(self, n_sets, block_size, associativity, pol):
        super().__init__(n_sets, block_size, associativity, pol)
        
        self._set_size = associativity

        self._validation_bits = [[0 for _ in range(self._set_size)] for _ in range(n_sets)]
        self._tags = [[0 for _ in range(self._set_size)] for _ in range(n_sets)]

        self._currently_empty = [0 for _ in range(n_sets)]
        self._replacement_spot = [0 for _ in range(n_sets)]     # Exclusivo do FIFO
        self._historic = [[] for _ in range(n_sets)]            # Exclusivo do LRU

    def _update__historic(self, tag, set_destiny) -> None:
        try:
            pos = self._historic[set_destiny].index(tag)
            del self._historic[set_destiny][pos]    
        except(ValueError):    
            pass    
        
        self._historic[set_destiny].insert(0, tag)

    def request(self, index: int, tag: int) -> bool:
        set_destiny = self._hash_function(index)
        empty_slot = self._currently_empty[set_destiny]

        if self.pol == 'l':
            self._update__historic(tag, set_destiny)

        if empty_slot < self._set_size:
            if tag not in self._tags[set_destiny][:empty_slot]:
                self._tags[set_destiny][empty_slot] = tag
                self._validation_bits[set_destiny][empty_slot] = 1

                self.errors['Compulsório'] += 1
                self._currently_empty[set_destiny] += 1
                return False
        else:
            if tag not in self._tags[set_destiny]:
                self._fault_treatment(tag, set_destiny)
                
                if not self._is_full():
                    self.errors['Conflito'] += 1
                    return False
                
                self.errors['Capacidade'] += 1
                return False
        
        self.hits += 1
        return True

    def _fault_treatment(self, tag: int, set_destiny: int):
        if self.pol == 'r':
            return self._random(tag, set_destiny)
        if self.pol == 'l':
            return self._lru(tag, set_destiny)
        if self.pol == 'f':
            return self._fifo(tag, set_destiny)
        
        raise ValueError('Política de substituição inválida!')
    
    def _random(self, tag: int, set_destiny: int) -> None:
        pos = random.randrange(0, self._set_size, step=1)
        self._tags[set_destiny][pos] = tag

    def _lru(self, tag: int, set_destiny: int) -> None:
        least_recent_tag = self._historic[set_destiny][-1]
        del self._historic[set_destiny][-1]

        pos = self._tags[set_destiny].index(least_recent_tag)
        self._tags[set_destiny][pos] = tag

    def _fifo(self, tag: int, set_destiny: int) -> None:
        pos = self._replacement_spot[set_destiny]
        
        self._tags[set_destiny][pos] = tag
        self._replacement_spot[set_destiny] += 1
        
        if self._replacement_spot[set_destiny] == self._set_size:
            self._replacement_spot[set_destiny] = 0

    def _is_full(self) -> bool:
        for size in self._currently_empty:
            if size == self._set_size:
                continue
            return False

        return True
        
class CacheFactory:
    def create_cache(self, n_sets: int, block_size: int, associativity: int, pol: str) -> Cache:
        if associativity == 1:
            return DirectMappingCache(n_sets, block_size, associativity, pol)
        
        return AssociativeMappingCache(n_sets, block_size, associativity, pol)
