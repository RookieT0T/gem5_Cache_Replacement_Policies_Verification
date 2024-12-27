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
            print(accesses)  

            # this list is the cache set containing multiple cache lines; head is LRU and tail is the MRU
            inCache = []
            hit, miss = 0, 0

            for a in accesses:
                if a in inCache:                # cache hit
                    hit += 1
                    # print(a)
                    inCache.remove(a)   
                    inCache.append(a)           # append a to the tail to be the MRU one
                
                else:                           # cache miss
                    miss += 1
                    if len(inCache) < 16:
                        inCache.insert(0, a)    # insert to the head to be the LRU one
                    else:
                        inCache.pop(0)          # eviction
                        inCache.insert(0, a)
        
            print(f"Testbench id: {id}")
            print(f"Miss: {miss}")
            print(f"Hit: {hit}\n")