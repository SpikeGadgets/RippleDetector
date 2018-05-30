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

#ifndef RIPPLE_FILTER_H
#define RIPPLE_FILTER_H

#ifdef __cplusplus
extern "C" {
#endif
#include <stdint.h>

///_PYTHONCFFI
/* Ripple detection classes/functions implemented in C. 
 * Implementation from Kemere Lab at Rice University 
 * https://www.biorxiv.org/content/biorxiv/early/2018/04/11/298661.full.pdf
 */ 


/* Ripple Filter
 * Bandpass 30 tap FIR filter followed by a lowpass 33 tap FIR filter
 */ 

// Struct ripple_filter_t holds coefficients and history
typedef struct _ripple_filter_t ripple_filter_t;

// Create new ripple filter
ripple_filter_t*        rfilter_new (void);

// Update filter with new int16 value, returning filtered value as double
double                  rfilter_update (ripple_filter_t* filter, int16_t data);

// Destroy ripple filter and set pointer to NULL
void                    rfilter_destroy (ripple_filter_t* filter);



/* Ripple Parameter Training
 * Basic mean and standard deviation calculations. 
 */ 

// Struct ripple_param_est_t holds 
typedef struct _ripple_params_t ripple_params_t;

// Create new ripple parameter estimator
ripple_params_t*     rparams_new (int datalen, double thresholdcontrol);

// Add value to parameter estimator. 
// - Parameters will be automatically calculated once number of data reaches `datalen`
// - If array has been filled and parameters calculated, any further calls 
//      will be ignored unless rparams_reset is called.
void                    rparams_update (ripple_params_t* params, double data);

// Resets the ripple parameters
void                    rparams_reset (ripple_params_t* params);

// Returns if the parameters has been estimated or not. 
int                     rparams_estimated (ripple_params_t* params);

// Returns the estimated mean
double                  rparams_mean (ripple_params_t* params);

// Returns the estimated standard deviation
double                  rparams_stdev (ripple_params_t* params);

// Returns the threshold a value has to exceed for a ripple to occur
double                  rparams_threshold(ripple_params_t* params);

// Destroy ripple parameter estimator and set pointer to NULL
void                    rparams_destroy (ripple_params_t* params);



/*
 *
 */

///_PYTHONCFFI
#ifdef __cplusplus
}
#endif

#endif