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

            # this list is the cache set containing multiple cache lines  
            inCache = []
            hit, miss = 0, 0
            # time tracking
            timestamp = 0
            timeDic = {}

            for a in accesses:
                timestamp += 1
                if a in inCache:
                    hit += 1
                    #print(a)
                    if a in timeDic:
                        timeDic[a] = timestamp
                    else:
                        print("error 3")
                else:
                    miss += 1

                    # the cache has 16-way-set associative and check if the cache set is full
                    if len(inCache) < 16:
                        inCache.append(a)
                        if a not in timeDic:
                            timeDic[a] = timestamp
                        else:
                            print("error 1")
                    else:
                        lru = min(inCache, key=lambda x: timeDic[x])                                    
                        inCache.remove(lru)         # evict the lru cache line from the cache set
                        del timeDic[lru]

                        inCache.append(a)
                        if a not in timeDic:
                            timeDic[a] = timestamp
                        else:
                            print("error 2")
                        
            print(f"Testbench id: {id}")
            print(f"Miss: {miss}")
            print(f"Hit: {hit}\n")