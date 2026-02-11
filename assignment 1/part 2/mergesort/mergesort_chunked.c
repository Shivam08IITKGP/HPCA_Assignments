#include <stdio.h>
#include <stdlib.h>

#define ARR_SIZE      2621440  // 10MB total
#define CHUNK_SIZE    524288   // 2MB chunks (ARR_SIZE / 5)

static int arr[ARR_SIZE];
static int temp[ARR_SIZE];

void merge(int *a, int left, int mid, int right)
{
    int i = left;
    int j = mid + 1;
    int k = left;

    while (i <= mid && j <= right) {
        if (a[i] <= a[j])
            temp[k++] = a[i++];
        else
            temp[k++] = a[j++];
    }

    while (i <= mid)
        temp[k++] = a[i++];

    while (j <= right)
        temp[k++] = a[j++];

    for (i = left; i <= right; i++)
        a[i] = temp[i];
}

void merge_sort_recursive(int *a, int left, int right)
{
    if (left < right) {
        int mid = left + (right - left) / 2;
        merge_sort_recursive(a, left, mid);
        merge_sort_recursive(a, mid + 1, right);
        merge(a, left, mid, right);
    }
}

int main()
{
    FILE *file = fopen("random_numbers.bin", "rb");
    if (!file)
        return 1;
    
    fread(arr, sizeof(int), ARR_SIZE, file);
    fclose(file);

    // Phase 1: Sort each 2MB chunk recursively (cache-friendly)
    // This processes 5 chunks of 524288 elements each
    for (int i = 0; i < ARR_SIZE; i += CHUNK_SIZE) {
        int chunk_start = i;
        int chunk_end = ((i + CHUNK_SIZE - 1) < (ARR_SIZE - 1)) ? (i + CHUNK_SIZE - 1) : (ARR_SIZE - 1);
        merge_sort_recursive(arr, chunk_start, chunk_end);
    }

    // Phase 2: Merge sorted chunks
    // Only 3 merge passes needed: 2MB->4MB, 4MB->8MB, 8MB->10MB
    for (int size = CHUNK_SIZE; size < ARR_SIZE; size *= 2) {
        for (int left = 0; left < ARR_SIZE; left += 2 * size) {
            int mid = left + size - 1;
            int right = left + 2 * size - 1;
            
            if (mid >= ARR_SIZE) 
                break;
            if (right >= ARR_SIZE) 
                right = ARR_SIZE - 1;
            
            merge(arr, left, mid, right);
        }
    }

    return 0;
}