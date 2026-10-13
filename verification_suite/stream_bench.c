#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main() {
    size_t n = 64 * 1024 * 1024; // 64 MB
    double *a = (double*)aligned_alloc(64, n);
    double *b = (double*)aligned_alloc(64, n);
    size_t elems = n / sizeof(double);
    for(size_t i=0; i<elems; ++i) { a[i] = 1.0; b[i] = 2.0; }
    
    // DRAM STREAM COPY (64 MB x 50 iters)
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for(int iter=0; iter<50; ++iter) {
        for(size_t i=0; i<elems; ++i) {
            b[i] = a[i] + 0.0001 * iter;
        }
        asm volatile("" : : "r"(b) : "memory");
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double dt_dram = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec)*1e-9;
    double bw_dram = (50.0 * n * 2.0) / dt_dram / 1e9;
    
    // L1 Cache Copy (16 KB = 2048 doubles x 500000 iters)
    size_t l1_elems = 2048;
    size_t l1_bytes = l1_elems * sizeof(double);
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for(int iter=0; iter<500000; ++iter) {
        for(size_t i=0; i<l1_elems; ++i) {
            b[i] = a[i] * 1.000001;
        }
        asm volatile("" : : "r"(b) : "memory");
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double dt_l1 = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec)*1e-9;
    double bw_l1 = (500000.0 * l1_bytes * 2.0) / dt_l1 / 1e9;
    
    printf("ALADIN_DDR4_STREAM_GBS=%.2f\nALADIN_L1_CACHE_GBS=%.2f\nCheck=%f\n", bw_dram, bw_l1, b[0]);
    free(a); free(b);
    return 0;
}
