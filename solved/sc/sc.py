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
            dic = {}
            hit, miss = 0, 0

            for a in accesses:
                if a in inCache:
                    hit += 1
                    #print(a)
                    if a in dic:
                        dic[a] = 1
                    else:
                        print("error 1")
                else:
                    miss += 1
                    # the cache has 16-way set associative and check if the cache set is full
                    if len(inCache) < 16:
                        inCache.append(a)
                        if a not in dic:
                            dic[a] = 0      # set default flag
                        else:
                            print("error 2")
                    else:
                        found = 0
                        index = -1
                        for i in range(16):
                            if(dic[inCache[i]] == 1):
                                dic[inCache[i]] = 0    # clear the second chance flag
                            else:
                                found = 1
                                index = i
                                break
                        
                        # victim found & do the conventional cache replacement
                        if found == 1 and index != -1:
                            del dic[inCache[index]]
                            inCache.remove(inCache[index])
                        else:
                            head = inCache.pop(0)
                            del dic[head]
                        inCache.append(a)
                        if a not in dic:
                            dic[a] = 0      # default flag
                        else:
                            print("error 3")

            print(f"Testbench id: {id}")
            print(f"Miss: {miss}")
            print(f"Hit: {hit}\n")