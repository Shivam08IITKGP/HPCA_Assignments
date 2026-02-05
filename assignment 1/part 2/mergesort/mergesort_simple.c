#include <stdio.h>
#include <stdlib.h>
.
#define ARR_SIZE 2621440

int arr[ARR_SIZE];
int temp[ARR_SIZE];

void merge(int arr[], int l, int m, int r) 
{
    int i = l;
    int j = m + 1;
    int k = l;

    while (i <= m && j <= r) 
    {
        if (arr[i] <= arr[j]) 
        {
            temp[k] = arr[i];
            i++;
        } 
        else 
        {
            temp[k] = arr[j];
            j++;
        }
        k++;
    }

    while (i <= m) 
    {
        temp[k] = arr[i];
        i++;
        k++;
    }

    while (j <= r) 
    {
        temp[k] = arr[j];
        j++;
        k++;
    }

    for (int p = l; p <= r; p++) 
    {
        arr[p] = temp[p];
    }
}

void mergeSort(int arr[], int l, int r) 
{
    if (l < r) 
    {
        int m = l + (r - l) / 2;
        mergeSort(arr, l, m);
        mergeSort(arr, m + 1, r);
        merge(arr, l, m, r);
    }
}

int main() {
    FILE *file = fopen("problem2/random_numbers.bin", "rb");
    if (!file) {
        file = fopen("random_numbers.bin", "rb");
        if (!file)
        {
            printf("Error opening file!\n");
            return 1;
        }
    }
    
    size_t result = fread(arr, sizeof(int), ARR_SIZE, file);
    fclose(file);

    printf("Starting Simple Merge Sort...\n");
    mergeSort(arr, 0, ARR_SIZE - 1);
    printf("Sorting Complete!\n");

    return 0;
}