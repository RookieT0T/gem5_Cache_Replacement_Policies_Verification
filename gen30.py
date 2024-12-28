import random
import os

# docker run --volume $(pwd):$(pwd) -w $(pwd) amd_vega  make -f Makefile

def generateMakefile(number, directory):
    build_rules = "\n".join(
        [
            f"\t$(CC) $(HIPOPTS) trial_{i}.cpp -o trial_{i} $(CFLAGS) $(LDFLAGS)"
            for i in range(number)
        ]
    )
    
    makefile_content = f"""
HIPOPTS = --amdgpu-target=gfx900,gfx906 --save-temps

HIP_PATH ?= /opt/rocm/hip

CC := $(HIP_PATH)/bin/hipcc

release:
{build_rules}

clean:
\trm -f *.o *~ $(EXE)

run:
\t./$(EXE)

profile:
\trocprof ./$(EXE)

events:
\trocprof --events elapsed_cycles_sm ./$(EXE)
"""

    with open(f"{directory}/Makefile", "w") as makefile:
        makefile.write(makefile_content)

def generate(pattern, patternAddr, fileName):
    # the first 10 instructions
    head20 = '\"s_waitcnt vmcnt(0) & lgkmcnt(0)\\n\\t\" \n\t\t\"buffer_wbinvl1\\n\\t\" \n\t\t\"flat_load_dwordx2 %[out0], %[in1] glc\\n\\t\"'
    tail = '"s_waitcnt vmcnt(0) & lgkmcnt(0)\\n\\t\" \n\t\t\"s_nop 0\\n\\t\"' 
    instructions20 = "\n\n\t\t".join(
        [
            f'\"s_waitcnt vmcnt(0) & lgkmcnt(0)\\n\\t\" \n\t\t"flat_load_dwordx2 %[out{i}], %[in{i + 1}] glc\\n\\t\"'
            for i in range(2, 20, 2)
        ]
    )
    final20 = head20 + "\n\n\t\t" + instructions20 + "\n\n\t\t" + tail

    outReg20 = ", ".join(
        [f'[out{i}]"=v"(a)' for i in range(0, 20, 2)]
    )

    inReg20 = ", ".join(
        [f'[in{i * 2 + 1}]"v"((uint64_t *)&arr[{patternAddr[i]}])' for i in range(0, 10)]
    )

    # /////////////////////// #
    # the second 10 instructions
    head40 = '\"s_waitcnt vmcnt(0) & lgkmcnt(0)\\n\\t\" \n\t\t\"buffer_wbinvl1\\n\\t\" \n\t\t\"flat_load_dwordx2 %[out20], %[in21] glc\\n\\t\"'
    instructions40 = "\n\n\t\t".join(
        [
            f'\"s_waitcnt vmcnt(0) & lgkmcnt(0)\\n\\t\" \n\t\t\"flat_load_dwordx2 %[out{i}], %[in{i + 1}] glc\\n\\t\"'
            for i in range(22, 40, 2)
        ]
    )
    final40 = head40 + "\n\n\t\t" + instructions40 + "\n\n\t\t" + tail
    
    outReg40 = ", ".join(
        [f'[out{i}]"=v"(b)' for i in range(20, 40, 2)]
    )

    inReg40 = ", ".join(
        [f'[in{i * 2 + 1}]"v"((uint64_t *)&arr[{patternAddr[i]}])' for i in range(10, 20)]
    )

    # /////////////////////// #
    # the third 10 instructions
    head60 = '\"s_waitcnt vmcnt(0) & lgkmcnt(0)\\n\\t\" \n\t\t\"buffer_wbinvl1\\n\\t\" \n\t\t\"flat_load_dwordx2 %[out40], %[in41] glc\\n\\t\"'
    instructions60 = "\n\n\t\t".join(
        [
            f'\"s_waitcnt vmcnt(0) & lgkmcnt(0)\\n\\t\" \n\t\t\"flat_load_dwordx2 %[out{i}], %[in{i + 1}] glc\\n\\t\"'
            for i in range(42, 60, 2)
        ]
    )
    final60 = head60 + "\n\n\t\t" + instructions60 + "\n\n\t\t" + tail
    
    outReg60 = ", ".join(
        [f'[out{i}]"=v"(c)' for i in range(40, 60, 2)]
    )

    inReg60 = ", ".join(
        [f'[in{i * 2 + 1}]"v"((uint64_t *)&arr[{patternAddr[i]}])' for i in range(20, 30)]
    )

    # contents written into the cpp file
    cpp = f"""
#include "hip/hip_runtime.h"
#define HCC_ENABLE_PRINTF
#include <stdio.h>
#include <stdlib.h>

#define CACHE_ENTRIES 4194304

// kernel code
// Access pattern: {', '.join(pattern)}
// Access count: {len(pattern)}

__global__ void kernel(int * arr) {{
    uint64_t a = 0, b = 0, c = 0;
    
    asm volatile(
        {final20}
        : {outReg20}
        : {inReg20}
        : "memory");

    asm volatile(
        {final40}
        : {outReg40}
        : {inReg40}
        : "memory");

    asm volatile(
        {final60}
        : {outReg60}
        : {inReg60}
        : "memory");
}}

int main(){{
    int *arr = (int *)calloc(sizeof(int), CACHE_ENTRIES);
    int *arr_g;

    hipMallocManaged(&arr_g, CACHE_ENTRIES*sizeof(int));
    hipMemcpy(arr_g, arr, CACHE_ENTRIES*sizeof(int), hipMemcpyHostToDevice);

    hipLaunchKernelGGL(kernel, dim3(1), dim3(1), 0, 0, arr_g);

    hipFree(arr_g);
    free(arr);
    return 0;
}}
    """

    # file generation
    with open(fileName, "w") as file:
        file.write(cpp)

directory = "./testbench"
os.makedirs(directory, exist_ok=True)
print(f"Directory {directory} is automatically generated.")
number = input("Enter the number of tests you want: ")
for n in range(int(number)):
    dic = {}                                # dictionary tracking the starting address of each cache line
    offset = [0] * 30                   
    notAccessed = []                    
    for i in range(30):
        notAccessed.append(f"c_{i}")        # the list storing the cache lines that have not been accessed
        dic[f"c_{i}"] = i * 65536           # associate each cache line label with the corresponding address

    # the first 16 accesses
    accessed = []                           # cache lines that are in the cache set
    pattern = []                            # access pattern 
    patternAddr = []                        # access address
    for i in range(16):
        temp = notAccessed.pop(0)
        accessed.append(temp)
        pattern.append(temp)
        patternAddr.append(dic[temp])

    # the rest of cache accesses
    for i in range(16, 30):
        value = random.choices([0, 1], weights=[35, 65], k=1)[0]       # random determinator
        #print(value)
        if value == 0:                      # 0 -> access other cache lines that have not been accessed
            temp = notAccessed.pop(0)
            pattern.append(temp)            # add this new access to the end of the access pattern list
            patternAddr.append(dic[temp])
            accessed.append(temp)
        else:                               # 1 -> reaccess or cache hit
            temp = random.choice(accessed)  # randomly pick an element from the accessed list
            pattern.append(temp)
            index = int(temp.split('_')[1])
            #print(index)
            offset[index] += 1
            patternAddr.append(dic[temp] + offset[index])
        
    #print(pattern)
    #print(patternAddr)
    '''
    for i in range(60):
        print(pattern[i])
        print(patternAddr[i])
    '''
    print(", ".join(pattern))
    #print(pattern)
    generate(pattern, patternAddr, f'{directory}/trial_{n}.cpp')
generateMakefile(int(number), directory)                            # generate the Makefile