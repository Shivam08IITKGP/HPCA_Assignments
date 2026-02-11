#include <stdio.h>
#include <stdlib.h>

#define ARR_SIZE 2621440  // 10MB

int arr[ARR_SIZE];
int temp[ARR_SIZE];

void merge(int arr[], int left, int mid, int right)
{
    int i = left;
    int j = mid + 1;
    int k = left;

    while (i <= mid && j <= right)
    {
        if (arr[i] <= arr[j])
            temp[k++] = arr[i++];
        else
            temp[k++] = arr[j++];
    }

    while (i <= mid)
        temp[k++] = arr[i++];

    while (j <= right)
        temp[k++] = arr[j++];

    for (int p = left; p <= right; p++)
        arr[p] = temp[p];
}

void mergeSort(int arr[], int left, int right)
{
    if (left < right)
    {
        int mid = left + (right - left) / 2;
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }
}

int main()
{
    FILE *file = fopen("random_numbers.bin", "rb");
    if (!file)
        return 1;

    fread(arr, sizeof(int), ARR_SIZE, file);
    fclose(file);

    mergeSort(arr, 0, ARR_SIZE - 1);

    return 0;
}