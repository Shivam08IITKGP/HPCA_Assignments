#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 1024

/* Global 2D array of double-precision floats */
double matrix[N][N];

int main()
{
    /* Fill matrix with random values */
    srand(42);
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            matrix[i][j] = (double)rand() / RAND_MAX;

    double sum = 0.0;

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    /* Row-major traversal */
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            sum += matrix[i][j];

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;

    printf("Row-major traversal time: %f seconds\n", elapsed);
    /* Print sum to prevent compiler from optimizing away the computation */
    printf("Ignore: %lf\n", sum);

    return 0;
}
