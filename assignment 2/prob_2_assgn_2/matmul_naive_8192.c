#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#define N 8192

/* Global 2D arrays of double-precision floats */
double Y[N][N];
double Z[N][N];
double X[N][N];

int main() {
    srand(42);
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            Y[i][j] = (double)rand() / RAND_MAX;
            Z[i][j] = (double)rand() / RAND_MAX;
        }
    memset(X, 0, sizeof(X));
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            for (int k = 0; k < N; k++)
                X[i][j] += Y[i][k] * Z[k][j];


    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec)
                   + (end.tv_nsec - start.tv_nsec) / 1e9;

    printf("Naive matrix multiplication time: %f seconds\n", elapsed);
    printf("Ignore: C[0][0] = %f\n", X[0][0]);

    return 0;
}