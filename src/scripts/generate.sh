#!/usr/bin/env bash

GRID_SIDE=10
N_ARIETY=3
N_NAME="grid"
ITERS=5

# Paths
dcop_path="/home/fioretto/Repos/MaxSum/"
data_path=${dcop_path}"data/"
scripts_path=${dcop_path}"scripts/"
# Exe
ccg_maker=${scripts_path}"wcsp"
dcop_gen=${scripts_path}"dcop_gen_rand.py"
dcop_gen_sf=${scripts_path}"dcop_gen_scalefree.py"
dcop_gen_grid=${scripts_path}"dcop_gen_grid.py"

ccg_to_dcop=${scripts_path}"ccg_to_dcop.py"
dcop_stats=${scripts_path}"postprocess_ccg.py"
pipeline_path=${scripts_path}"code/"
ccg_solver=${pipeline_path}"wcsp-solver"

# Generate Random WCSP
file=$N_NAME

#######################
# Create instance
#######################

# Grid
for i in {1..30}; do

    # for n in 5 10 15 20 25; do
    #     python $dcop_gen_grid -a $n -r 3 -c 100 -n "grid" -o ${data_path}"/grid/grid_${n}_${i}"
    # done

    # for n in 50 100 150 200 250; do
    #     python $dcop_gen_sf -a $n -r 3 -c 100 -n "sf" -o ${data_path}"/sf/sf_${n}_${i}"
    # done

    for n in 100; do
        out_val=$(python $dcop_gen -a $n -d 2 -p 0.4 -r 3 -c 100 -n "rand" -o ${data_path}"/rand4_h/rand4_h_${n}_${i}")
        fail="sanity check failed!"
        if [ "$out_val" == "$fail" ]; then
            echo "Error in generating rand_${n}_${i}"
        fi

        out_val=$(python $dcop_gen -a $n -d 2 -p 0.8 -r 3 -c 100 -n "rand" -o ${data_path}"/rand8_h/rand8_h_${n}_${i}")
        fail="sanity check failed!"
        if [ "$out_val" == "$fail" ]; then
            echo "Error in generating rand_${n}_${i}"
        fi
    done

done
