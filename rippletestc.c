#include "ripplefilter.h"
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <stdio.h>
void performanceTest(int nints){
    ripple_filter_t* filter = rfilter_new();
    ripple_params_t* params = rparams_new(nints);
    int16_t *ints = (int16_t*)malloc(sizeof(int16_t)*nints);
    int i;
    for(i = 0; i < nints; ++i){
        ints[i] = rand() % (2^16) - (2^16)/2;
    }

    double val = 0.0;
    struct timespec before, after;
    clock_gettime(CLOCK_MONOTONIC, &before);
    for(i = 0; i < nints; ++i){
        val = rfilter_update(filter, ints[i]);
        rparams_update(params, val);
    }
    clock_gettime(CLOCK_MONOTONIC, &after);

    long msecs = (double)(after.tv_nsec - before.tv_nsec)/1000000.0;
    printf("Filtering %d random ints: %ld msecs\n", nints, msecs);
    printf("Params: Mean: %f. Stdev: %f\n", rparams_mean(params), rparams_stdev(params));

    rfilter_destroy(filter);
    rparams_destroy(params);
    free(ints);
}

void correctnessTest(const char* infile, const char* outfile){
    FILE *inf = fopen(infile, "r");
    FILE *outf = fopen(outfile,"w");
    if(inf && outf){
        char* line = NULL;
        ripple_filter_t *filter = rfilter_new();
        ssize_t read;
        size_t len;
        while((read = getline(&line, &len, inf)) != -1 ){
            fprintf(outf, "%f\n", rfilter_update(filter, atoi(line)));
        }
        if(line) free(line);
        fclose(inf);
        fclose(outf);
        rfilter_destroy(filter);
    } 
}

int main(int argc, char **argv){
    // correctnessTest("../input.txt", "cout.txt");

    if(argc > 1){
        for(int i = 1; i < argc; i++){
            performanceTest(atoi(argv[i]));
        }
    }
    else{
        performanceTest(30000);
    }
    return 0;
}