#include <stdlib.h>

// 10MB total data / 4 bytes per int = 2,621,440 ints
#define ARRAY_LENGTH 2621440
#define SEED 42

void merge_arrays(int *data, int *buffer, int start, int middle, int end)
{
    int left_ptr = start;
    int right_ptr = middle + 1;
    int buffer_ptr = start;

    while (left_ptr <= middle && right_ptr <= end) {
        buffer[buffer_ptr++] = (data[left_ptr] <= data[right_ptr]) 
                                ? data[left_ptr++] 
                                : data[right_ptr++];
    }

    while (left_ptr <= middle) {
        buffer[buffer_ptr++] = data[left_ptr++];
    }

    while (right_ptr <= end) {
        buffer[buffer_ptr++] = data[right_ptr++];
    }

    for (int i = start; i <= end; i++) {
        data[i] = buffer[i];
    }
}

void recursive_merge_sort(int *data, int *buffer, int start, int end)
{
    if (start >= end) return;
    int middle = start + (end - start) / 2;
    recursive_merge_sort(data, buffer, start, middle);
    recursive_merge_sort(data, buffer, middle + 1, end);
    merge_arrays(data, buffer, start, middle, end);
}

int main(void)
{
    int *dataset = malloc(ARRAY_LENGTH * sizeof(int));
    int *workspace = malloc(ARRAY_LENGTH * sizeof(int));
    
    if (!dataset || !workspace) return 1;

    // Generate same random sequence in-memory
    srand(SEED);
    for(int i = 0; i < ARRAY_LENGTH; i++) {
        dataset[i] = rand();
    }

    // Run the sort
    recursive_merge_sort(dataset, workspace, 0, ARRAY_LENGTH - 1);

    free(dataset);
    free(workspace);
    return 0;
}