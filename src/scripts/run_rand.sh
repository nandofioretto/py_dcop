#!/usr/bin/env bash
exp=$1

# Paths
dcop_path="/home/fioretto/Repos/MaxSum/"
data_path=${dcop_path}"data/"
scripts_path=${dcop_path}"scripts/"


#######################
# Create instance
#######################

# Grid
if [ "$exp" == "grid" ]; then
    for n in 5 10 15 20 25; do
        for i in {1..30}; do
            echo "running Grid $n $i"
            ${scripts_path}/exe_ccg_grid.sh "grid" $n $i > $data_path/"out/grid/out_${n}_${i}.out"
        done
    done
fi

if [ "$exp" == "sf" ]; then
    for n in 50 100 150 200 250; do
        for i in {1..30}; do
            echo "running Sf $n $i"
            ${scripts_path}/exe_ccg_sf.sh "sf" $n $i > $data_path/"out/sf/out_${n}_${i}.out"
        done
    done
fi
  
if [ "$exp" == "rand4" ]; then
    for n in 100; do
        for i in {1..10}; do
	    if [ -f $data_path/"rand4/rand4_${n}_${i}.wcsp" ]; then
		echo "running Rand4 $n $i"
		${scripts_path}/exe_ccg_rand.sh "rand4" $n $i > $data_path/"out/rand4/out_${n}_${i}.out"
	    fi
        done
    done
fi

if [ "$exp" == "rand8" ]; then
    for n in 100; do
        for i in {1..20}; do
	    if [ -f $data_path/"rand8/rand8_${n}_${i}.wcsp" ]; then
		echo "running Rand8 $n $i"
		${scripts_path}/exe_ccg_rand.sh "rand8" $n $i > $data_path/"out/rand8/out_${n}_${i}.out"
	    fi
        done
    done
fi

if [ "$exp" == "rand4d" ]; then
    for n in 150; do
        for i in {1..10}; do
	    if [ -f $data_path/"rand4/rand4_${n}_${i}.wcsp" ]; then
		echo "running Rand4d $n $i"
		${scripts_path}/test.sh "rand4" $n $i > $data_path/"out/rand4/out_d_${n}_${i}.out"
	    fi
        done
    done
fi

if [ "$exp" == "rand8d" ]; then
    for n in 100; do
        for i in {1..20}; do
	    if [ -f $data_path/"rand8/rand8_${n}_${i}.wcsp" ]; then
		echo "running Rand8d $n $i"
		${scripts_path}/test.sh "rand8" $n $i > $data_path/"out/rand8/out_d_${n}_${i}.out"
	    fi
        done
    done
fi
