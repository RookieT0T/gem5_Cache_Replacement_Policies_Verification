with open("./accessPatterns.txt", 'r') as file:
    id = 0
    for line in file:
        '''
        if 'After the manual verification' in line:
            break
        '''
        if not line.strip():
            continue

        if '#' not in line:
            id += 1
            # accessess list stores the all cache accesses
            accesses = [item.strip() for item in line.strip().split(',')]    
            # print(accesses)  
            # this list is the cache set containing multiple cache lines  
            inCache = []
            hit, miss = 0, 0
            for a in accesses:
                if a in inCache:
                    hit += 1
                else:
                    miss += 1
                    # the cache has 16-way set associative and check if the cache set is full
                    if len(inCache) < 16:
                        inCache.append(a)
                    else:
                        item = inCache.pop(0)     # pop the cache line in the beginning because of how fifo works
                        inCache.append(a)
            print(f"Testbench id: {id}")
            print(f"Miss: {miss}")
            print(f"Hit: {hit}\n")