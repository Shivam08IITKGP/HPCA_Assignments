#include <stdlib.h>
#include <stdio.h>

// 10MB total data / 4 bytes per int = 2,621,440 ints
#define TOTAL_ELEMENTS 2621440
#define ELEMENTS_PER_CHUNK 524288
#define TOTAL_CHUNKS 5
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
    // Pre-allocate all memory
    int *chunk_arrays[TOTAL_CHUNKS];
    int *temp_buffer = malloc(ELEMENTS_PER_CHUNK * sizeof(int));
    if (!temp_buffer) return 1;

    // Phase 1: Generate and Sort Chunks
    srand(SEED); 
    
    for (int chunk_id = 0; chunk_id < TOTAL_CHUNKS; chunk_id++) {
        chunk_arrays[chunk_id] = malloc(ELEMENTS_PER_CHUNK * sizeof(int));
        if (!chunk_arrays[chunk_id]) return 1;

        for(int i = 0; i < ELEMENTS_PER_CHUNK; i++) {
            chunk_arrays[chunk_id][i] = rand();
        }

        recursive_merge_sort(chunk_arrays[chunk_id], temp_buffer, 
                           0, ELEMENTS_PER_CHUNK - 1);
    }
    
    free(temp_buffer);

    // Phase 2: K-Way Merge
    int *final_output = malloc(TOTAL_ELEMENTS * sizeof(int));
    if (!final_output) return 1;
    
    int chunk_positions[TOTAL_CHUNKS] = {0};

    for (int output_idx = 0; output_idx < TOTAL_ELEMENTS; output_idx++) {
        int selected_chunk = -1;
        int minimum_value = 0;

        for (int chunk_id = 0; chunk_id < TOTAL_CHUNKS; chunk_id++) {
            if (chunk_positions[chunk_id] < ELEMENTS_PER_CHUNK) {
                int current_value = chunk_arrays[chunk_id][chunk_positions[chunk_id]];
                if (selected_chunk == -1 || current_value < minimum_value) {
                    minimum_value = current_value;
                    selected_chunk = chunk_id;
                }
            }
        }

        final_output[output_idx] = minimum_value;
        chunk_positions[selected_chunk]++;
    }

    for (int i = 0; i < TOTAL_CHUNKS; i++) free(chunk_arrays[i]);
    free(final_output);

    return 0;
}