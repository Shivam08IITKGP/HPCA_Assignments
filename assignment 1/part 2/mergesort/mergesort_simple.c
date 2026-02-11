#include <stdio.h>
#include <stdlib.h>

/*
    This version reads the entire dataset at once
    and performs a standard recursive merge sort.
*/

#define TOTAL_NUMBERS 2621440


/* Merge two sorted halves inside arr[] */
void merge(int *arr, int *temp, int left, int mid, int right)
{
    int i = left;        // pointer for left half
    int j = mid + 1;     // pointer for right half
    int k = left;        // pointer for temp array

    // Compare elements from both halves
    while (i <= mid && j <= right) {
        if (arr[i] <= arr[j])
            temp[k++] = arr[i++];
        else
            temp[k++] = arr[j++];
    }

    // Copy any remaining elements
    while (i <= mid)
        temp[k++] = arr[i++];

    while (j <= right)
        temp[k++] = arr[j++];

    // Copy merged section back into original array
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

    // Allocate memory for full dataset
    int *numbers = malloc(TOTAL_NUMBERS * sizeof(int));
    int *temp = malloc(TOTAL_NUMBERS * sizeof(int));

    if (!numbers || !temp) {
        printf("Memory allocation failed.\n");
        fclose(fp);
        free(numbers);
        free(temp);
        return 1;
    }

    // Read entire file into memory
    size_t read_count = fread(numbers, sizeof(int),
                              TOTAL_NUMBERS, fp);

    if (read_count != TOTAL_NUMBERS) {
        printf("Error while reading file.\n");
        fclose(fp);
        free(numbers);
        free(temp);
        return 1;
    }

    fclose(fp);

    // Perform merge sort on full dataset
    merge_sort(numbers, temp, 0, TOTAL_NUMBERS - 1);

    free(numbers);
    free(temp);

    return 0;
}
