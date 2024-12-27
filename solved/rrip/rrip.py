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
            counter = {}
            hit, miss = 0, 0

            for a in accesses:
                if a in inCache:
                    hit += 1
                    # print(a)
                    counter[a] = max(counter[a] - 1, 0)
                else:
                    miss += 1
                    # the cache has 16-way set associative and check if the cache set is full
                    if len(inCache) < 16:
                        inCache.append(a)
                        if a not in counter:
                            counter[a] = 2
                        else:
                            print("error 1")
                    else:
                        counterMax = max(counter.values())
                        for i in range(16):
                            if(counter[inCache[i]] == counterMax):
                                del counter[inCache[i]]
                                inCache[i] = a  # replacement
                                
                                # update counters of other cache lines
                                diff = 3 - counterMax
                                if diff > 0:
                                    for key in counter:
                                        counter[key] = min(counter[key] + diff, 3)

                                # then, insert the new one
                                if a not in counter:
                                    counter[a] = 2
                                else:
                                    print("error 1")
                                break

            print(f"Testbench id: {id}")
            print(f"Miss: {miss}")
            print(f"Hit: {hit}\n")