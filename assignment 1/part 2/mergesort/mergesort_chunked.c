#include <stdio.h>
#include <stdlib.h>

/*
    We have ~2.6M integers.
    Instead of sorting everything at once,
    we divide the data into 5 chunks and sort each chunk separately.
*/

#define TOTAL_NUMBERS     2621440
#define CHUNK_SIZE        524288
#define NUM_CHUNKS        5

void merge(int *arr, int *temp, int left, int mid, int right)
{
    int i = left;        
    int j = mid + 1;     
    int k = left;        
    
    while (i <= mid && j <= right) {
        if (arr[i] <= arr[j])
            temp[k++] = arr[i++];
        else
            temp[k++] = arr[j++];
    }

    
    while (i <= mid)
        temp[k++] = arr[i++];

    while (j <= right)
        temp[k++] = arr[j++];

    
    for (int x = left; x <= right; x++)
        arr[x] = temp[x];
}


/* Standard recursive merge sort */
void merge_sort(int *arr, int *temp, int left, int right)
{
    if (left >= right)
        return;

    int mid = left + (right - left) / 2;

    merge_sort(arr, temp, left, mid);
    merge_sort(arr, temp, mid + 1, right);

    merge(arr, temp, left, mid, right);
}


int main(void)
{
    FILE *fp = fopen("random_numbers.bin", "rb");
    if (!fp) {
        printf("Error: Could not open input file.\n");
        return 1;
    }

    
    int *chunks[NUM_CHUNKS];
    int *temp = malloc(CHUNK_SIZE * sizeof(int));
    if (!temp) {
        printf("Memory allocation failed.\n");
        fclose(fp);
        return 1;
    }

    
    for (int c = 0; c < NUM_CHUNKS; c++) {

        chunks[c] = malloc(CHUNK_SIZE * sizeof(int));
        if (!chunks[c]) {
            printf("Memory allocation failed for chunk %d\n", c);
            return 1;
        }

        size_t read_count = fread(chunks[c], sizeof(int),
                                  CHUNK_SIZE, fp);

        if (read_count != CHUNK_SIZE) {
            printf("Error while reading file.\n");
            fclose(fp);
            return 1;
        }

        
        merge_sort(chunks[c], temp, 0, CHUNK_SIZE - 1);
    }

    fclose(fp);
    free(temp);

    /*
        Now all 5 chunks are sorted.
        Next step: merge them together (k-way merge).
    */

    int *sorted_output = malloc(TOTAL_NUMBERS * sizeof(int));
    if (!sorted_output) {
        printf("Final allocation failed.\n");
        return 1;
    }

    int index_in_chunk[NUM_CHUNKS] = {0};

    
    for (int i = 0; i < TOTAL_NUMBERS; i++) {

        int chosen_chunk = -1;
        int smallest = 0;

        for (int c = 0; c < NUM_CHUNKS; c++) {

            if (index_in_chunk[c] < CHUNK_SIZE) {

                int value = chunks[c][index_in_chunk[c]];

                if (chosen_chunk == -1 || value < smallest) {
                    smallest = value;
                    chosen_chunk = c;
                }
            }
        }

        sorted_output[i] = smallest;
        index_in_chunk[chosen_chunk]++;
    }

    
    for (int c = 0; c < NUM_CHUNKS; c++)
        free(chunks[c]);

    free(sorted_output);

    return 0;
}
