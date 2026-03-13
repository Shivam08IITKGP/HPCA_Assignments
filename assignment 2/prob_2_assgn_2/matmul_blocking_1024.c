#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 1024
#define B 32   /* Block size */

/* Global 2D arrays of double-precision floats */
double Y[N][N];
double Z[N][N];
double X[N][N];

int main() {
    /* Fill Y and Z with random values */
    srand(42);
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            Y[i][j] = (double)rand() / RAND_MAX;
            Z[i][j] = (double)rand() / RAND_MAX;
        }

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    /* Blocked matrix multiplication: X = Y * Z, block size B */
    for (int ii = 0; ii < N; ii += B)
        for (int jj = 0; jj < N; jj += B)
            for (int kk = 0; kk < N; kk += B)
                /* Multiply B x B sub-blocks */
                for (int i = ii; i < ii + B && i < N; i++)
                    for (int j = jj; j < jj + B && j < N; j++)
                        for (int k = kk; k < kk + B && k < N; k++)
                            X[i][j] += Y[i][k] * Z[k][j];

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec)
                   + (end.tv_nsec - start.tv_nsec) / 1e9;

    printf("Blocked matrix multiplication time: %f seconds\n", elapsed);
    /* Print result to prevent compiler optimizing away the computation */
    printf("Ignore: C[0][0] = %f\n", X[0][0]);

    return 0;
}
