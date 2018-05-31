/*
# Copyright (C) 2018 SpikeGadgets, Kevin Wang kevin@spikegadgets.com

# This program is free software: you can redistribute it and/or modify
#                                it under the terms of the GNU General Public License as published by
#                                the Free Software Foundation, either version 3 of the License, or
#                                (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
#include "ripplefilter.h"
///_PYTHONCFFI
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <limits.h>
#define BPTAPS 30
#define LPTAPS 33

static const double filter_taps_bp[BPTAPS] = {
        0.006948895259200861,
        0.006926234072844102,
        0.006103502157617292,
        0.0019015869720564772,
        -0.008189119502501823,
        -0.024718456919193797,
        -0.04490236458710298,
        -0.06261768142301635,
        -0.07007106773169292,
        -0.060682222621851856,
        -0.03208366436487348,
        0.012060663184185196,
        0.0623490476891361,
        0.10616912299101257,
        0.131657880645337,
        0.13165788064533704,
        0.10616912299101257,
        0.06234904768913609,
        0.0120606631841852,
        -0.03208366436487348,
        -0.06068222262185186,
        -0.07007106773169292,
        -0.06261768142301641,
        -0.04490236458710301,
        -0.024718456919193794,
        -0.00818911950250182,
        0.0019015869720564766,
        0.0061035021576172944,
        0.006926234072844102,
        0.006948895259200861
};

static const double filter_taps_lp[LPTAPS] = {
        0.0203770957,
        0.0108532903,
        0.0134954582,
        0.0163441640,
        0.0193546202,
        0.0224738014,
        0.0256417906,
        0.0287934511,
        0.0318603667,
        0.0347729778,
        0.0374628330,
        0.0398648671,
        0.0419196133,
        0.0435752600,
        0.0447894668,
        0.0455308624,
        0.0457801628,
        0.0455308624,
        0.0447894668,
        0.0435752600,
        0.0419196133,
        0.0398648671,
        0.0374628330,
        0.0347729778,
        0.0318603667,
        0.0287934511,
        0.0256417906,
        0.0224738014,
        0.0193546202,
        0.0163441640,
        0.0134954582,
        0.0108532903,
        0.0203770957
    };

static const int16_t intfilter_taps_bp[BPTAPS] = {
228, 227, 200, 62, -268,  -810, -1471, -2052, -2296,-1988, 
-1051, 395, 2043, 3479, 4314, 4314, 3479, 2043,395, -1051, 
-1988, -2296, -2052, -1471, -810, -268, 62, 200, 227, 228
};

static const int16_t intfilter_taps_lp[LPTAPS] = {
668,  356,  442,  536,  634,  736,  840,  944, 1044, 1139, 1228,
1306, 1374, 1428, 1468, 1492, 1500, 1492, 1468, 1428, 1374, 1306,
1228, 1139, 1044,  944,  840,  736,  634,  536,  442,  356,  668
};

static int16_t sabs(int16_t i){
    int16_t res;
    if (SHRT_MIN == i)
        res = SHRT_MAX;
    else
        res = i < 0 ? -i : i;
    return res;
}
// ***********************************************************
struct _ripple_filter_t{
    double bp_in[BPTAPS];
    double lp_in[LPTAPS];
    int buff_loc_bp, buff_loc_lp;
};

ripple_filter_t* rfilter_new(void){
    ripple_filter_t* filt = (ripple_filter_t*)malloc(sizeof(ripple_filter_t));
    if(filt == NULL)
        return NULL;
    filt->buff_loc_bp = 0;
    filt->buff_loc_lp = 0;
    memset(filt->bp_in, 0, BPTAPS*sizeof(double));
    memset(filt->lp_in, 0, LPTAPS*sizeof(double));
    return filt;
}

double rfilter_update(ripple_filter_t* filt, int16_t data){
    //Bandpass filter
    double out = 0;

    double *buf_val = filt->bp_in + filt->buff_loc_bp;
    *buf_val = data;
    const double *coeff = filter_taps_bp;
    const double *coeff_end = filter_taps_bp + BPTAPS/*num filter taps*/;

    while(buf_val >= filt->bp_in){
        out += (*buf_val--) * (*coeff++);
    }
    buf_val = filt->bp_in + BPTAPS/*num filter taps*/-1;
    while(coeff < coeff_end){
        out += (*buf_val--) * (*coeff++);
    }
    if(++filt->buff_loc_bp >= BPTAPS/*num filter taps*/)
        filt->buff_loc_bp = 0;


    //Lowpass filter
    double *buf_val_lp = filt->lp_in+filt->buff_loc_lp;
    *buf_val_lp = fabs(out);
    out = 0;
    const double *coeff_lp = filter_taps_lp;
    const double *coeff_end_lp = filter_taps_lp + LPTAPS/*num filter taps*/;
    while(buf_val_lp >= filt->lp_in){
        out += (*buf_val_lp--) * (*coeff_lp++);
    }
    buf_val_lp = filt->lp_in + LPTAPS/*num filter taps*/-1;
    while(coeff_lp < coeff_end_lp){
        out += (*buf_val_lp--) * (*coeff_lp++);
    }

    if(++filt->buff_loc_lp >= LPTAPS/*num filter taps*/)
        filt->buff_loc_lp = 0;

    if(isnan(out)){
        out = 0; //replace NaNs with zeros. only reason NaNs should happen here is if the input is fully attenuated by the filter (from what I can gather)
    }

    return out;
}

void rfilter_destroy(ripple_filter_t* filter){
    free(filter);
}

// ***********************************************************
struct _ripple_intfilter_t{
    int16_t bp_in[BPTAPS];
    int16_t lp_in[LPTAPS];
    int buff_loc_bp, buff_loc_lp;
};

ripple_intfilter_t* rintfilter_new(void){
    ripple_intfilter_t* filt = (ripple_intfilter_t*)malloc(sizeof(ripple_intfilter_t));
    if(filt == NULL)
        return NULL;
    filt->buff_loc_bp = 0;
    filt->buff_loc_lp = 0;
    memset(filt->bp_in, 0, BPTAPS*sizeof(int16_t));
    memset(filt->lp_in, 0, LPTAPS*sizeof(int16_t));
    return filt;
}

int16_t rintfilter_update(ripple_intfilter_t* filt, int16_t data){
    //https://sestevenson.wordpress.com/2009/10/08/implementation-of-fir-filtering-in-c-part-2/
    //
    int32_t out = 1 << 14;

    //Bandpass filter
    int16_t *buf_val = filt->bp_in + filt->buff_loc_bp;
    *buf_val = data;
    const int16_t *coeff = intfilter_taps_bp;
    const int16_t *coeff_end = intfilter_taps_bp + BPTAPS/*num filter taps*/;

    while(buf_val >= filt->bp_in){
        out += (int32_t)(*buf_val--) * (int32_t)(*coeff++);
    }
    buf_val = filt->bp_in + BPTAPS/*num filter taps*/-1;
    while(coeff < coeff_end){
        out += (int32_t)(*buf_val--) * (int32_t)(*coeff++);
    }
    if(++filt->buff_loc_bp >= BPTAPS/*num filter taps*/)
        filt->buff_loc_bp = 0;


    //Lowpass filter
    int16_t *buf_val_lp = filt->lp_in+filt->buff_loc_lp;
    *buf_val_lp = sabs((int16_t)(out >> 15));
    out = 1<<14;
    const int16_t *coeff_lp = intfilter_taps_lp;
    const int16_t *coeff_end_lp = intfilter_taps_lp + LPTAPS/*num filter taps*/;
    while(buf_val_lp >= filt->lp_in){
        out += (int32_t)(*buf_val_lp--) * (int32_t)(*coeff_lp++);
    }
    buf_val_lp = filt->lp_in + LPTAPS/*num filter taps*/-1;
    while(coeff_lp < coeff_end_lp){
        out += (int32_t)(*buf_val_lp--) * (int32_t)(*coeff_lp++);
    }

    if(++filt->buff_loc_lp >= LPTAPS/*num filter taps*/)
        filt->buff_loc_lp = 0;

    return (int16_t)(out>>15);
}

void rintfilter_destroy(ripple_intfilter_t *filter){
    free(filter);
}

// ***********************************************************
struct _ripple_params_t{
    double *datavec;
    double threshcontrol;
    int datalen;
    int cur;
    double mean;
    double stdev;
    double ripplethresh;
};

ripple_params_t* rparams_new (int datalen, double thresholdcontrol){
    if(datalen <= 0)
        return NULL;

    ripple_params_t* params = (ripple_params_t*)malloc(sizeof(ripple_params_t));
    if(params == NULL)
        return NULL;

    params->datalen = datalen;
    params->cur = 0;
    params->datavec = (double*)malloc(sizeof(double)*datalen);
    if(params->datavec == NULL){
        free(params);
        return NULL;
    }
    params->mean = 0.0;
    params->stdev = 0.0;
    params->threshcontrol = thresholdcontrol;
    return params;
}

void rparams_update (ripple_params_t* params, double data){
    if(params->cur>= params->datalen){
        return;
    }
    
    //append data
    params->datavec[params->cur] = data;
    ++params->cur;

    //calc params
    if(params->cur == params->datalen){
        params->mean = 0.0;
        params->stdev = 0.0;
        
        //calc mean
        int i = 0;
        for(; i < params->datalen; ++i){
            params->mean += params->datavec[i];
        }
        params->mean /= (double)params->datalen;

        //calc stdev
        i = 0;
        for(; i < params->datalen; ++i){
            params->stdev += (params->datavec[i]-params->mean) * (params->datavec[i]-params->mean);
        }
        params->stdev /= (double)params->datalen;
        params->stdev = sqrt(params->stdev);

        //calc threshold
        params->ripplethresh = params->mean + params->threshcontrol * params->stdev;
    }
}

void rparams_reset (ripple_params_t* params){
    params->cur = 0;
    params->mean = 0.0;
    params->stdev = 0.0;
}

int rparams_estimated (ripple_params_t* params){
    return params->cur >= params->datalen;
}

double rparams_mean (ripple_params_t* params){
    return params->mean;
}

double rparams_stdev (ripple_params_t* params){
    return params->stdev;
}

double rparams_threshold(ripple_params_t* params){
    return params->ripplethresh;
}

void rparams_destroy (ripple_params_t* params){
    free(params->datavec);
    free(params);
}