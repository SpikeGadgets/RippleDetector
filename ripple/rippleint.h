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

#ifndef RIPPLE_INT_H
#define RIPPLE_INT_H

#ifdef __cplusplus
extern "C" {
#endif
#include <stdint.h>

///_PYTHONCFFI
/* Ripple detection classes/functions implemented in C. 
 * Implementation from Kemere Lab at Rice University 
 * https://www.biorxiv.org/content/biorxiv/early/2018/04/11/298661.full.pdf
 */ 

// Struct ripple_manager_t manages detectors across multiple channels
typedef struct _ripple_intmanager_t ripple_intmanager_t;

// Struct ripple_detector_t detects ripples for one channel
typedef struct _ripple_intdetector_t ripple_intdetector_t;

// Struct ripple_filter_t holds coefficients and history
typedef struct _ripple_intfilter_t ripple_intfilter_t;

// Struct ripple_param_est_t holds 
typedef struct _ripple_intparams_t ripple_intparams_t;


/* Multi channel ripple detector manager
 * Manages multiple detectors and checks ripples across them
 * Also can be configured to take in position data
 */
// Create new ripple manager
ripple_intmanager_t*       rmanager_new (int ntrodes, int mindetected, int trainingsamples, int sdthreshold, int samplehistory);

// // Enable or disable using velocity calculations in detection
// void                    rmanager_useposition(ripple_intmanager_t* manager, unsigned char enable, double velocitythresh);

// // Update position data. Converts to velocity, to be used in determining
// void                    rmanager_position(ripple_intmanager_t* manager, int16_t x, int16_t y);

// Update all ntrodes' lfp data. Data must be of length ntrodes, and values will be directly fed into detectors
void                    rmanager_lfpdata (ripple_intmanager_t* manager, int16_t *data);

// Checks for ripples given current state of manager
int                     rmanager_checkripples(ripple_intmanager_t* manager);

// Resets all data
void                    rmanager_reset(ripple_intmanager_t* manager);

// Destroy ripple manager
void                    rmanager_destroy (ripple_intmanager_t* manager);


/* Single channel ripple detector
 * Filters, trains, and checks threshold
 */ 
// Create new ripple detector
ripple_intdetector_t*      rdetector_new (int trainingsamples, int sdthreshold);

// Update filters. If training, train. If detecting, check threshold
unsigned char           rdetector_detect (ripple_intdetector_t* detector, int16_t data);

// Reset detector
void                    rdetector_reset(ripple_intdetector_t* detector);

// Destroy ripple detector and set pointer to NULL
void                    rdetector_destroy (ripple_intdetector_t* detector);



/* Integer only Ripple Filter
 * Bandpass 30 tap FIR filter followed by a lowpass 33 tap FIR filter
 */ 
// Create new ripple filter
ripple_intfilter_t*     rintfilter_new (void);

// Update filter with new int16 value, returning filtered value as double
int16_t                 rintfilter_update (ripple_intfilter_t* filter, int16_t data);

// Destroy ripple filter and set pointer to NULL
void                    rintfilter_destroy (ripple_intfilter_t* filter);



/* Ripple Parameter Training
 * Basic mean and standard deviation calculations. 
 */ 
// Create new ripple parameter estimator
ripple_intparams_t*     rintparams_new (int datalen, int thresholdcontrol);

// Add value to parameter estimator. 
// - Parameters will be automatically calculated once number of data reaches `datalen`
// - If array has been filled and parameters calculated, any further calls 
//      will be ignored unless rintparams_reset is called.
void                    rintparams_update (ripple_intparams_t* params, int16_t data);

// Resets the ripple parameters
void                    rintparams_reset (ripple_intparams_t* params);

// Returns if the parameters has been estimated or not. 
int                     rintparams_estimated (ripple_intparams_t* params);

// Returns the estimated mean
int16_t                 rintparams_mean (ripple_intparams_t* params);

// Returns the estimated standard deviation
int16_t                 rintparams_stdev (ripple_intparams_t* params);

// Returns the threshold a value has to exceed for a ripple to occur
int16_t                 rintparams_threshold(ripple_intparams_t* params);

// Destroy ripple parameter estimator and set pointer to NULL
void                    rintparams_destroy (ripple_intparams_t* params);



/*
 *
 */

///_PYTHONCFFI
#ifdef __cplusplus
}
#endif

#endif