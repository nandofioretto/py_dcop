#!/usr/bin/env bash

algorithms=("dsa" "maxsum" "ccg-maxsum" "ccg-maxsum-c" "ccg-dsa"  "dsa&ccg-maxsum" "dsa&ccg-maxsum-c" "dsa&ccg-dsa"  "ccg-maxsum+k")
py_dcop_home="/Users/ferdinandofioretto/Repos/dcop-ccg"
data_path="${py_dcop_home}/data"

num_agents=(10 50 100)
dom_size=(2 3 5)
seeds=(1 2 3 4 5 6 7 8 9 10)
gtypes=("rand-sparse" "rand-dense" "sf" "grid")

cmd="python src/py_dcop2.py"

cd ${py_dcop_home}
source venv/bin/activate

for s in ${seeds[@]}; do
	for gtype in ${gtypes[@]}; do
		for na in ${num_agents[@]}; do
			for nd in ${dom_size[@]}; do
				dcop_file="${data_path}/Feb20/in/${gtype}/agt_${na}_dom_${nd}_${s}.json"
				$cmd --nagents=$na --domsize=${nd} --graph=${gtype} --seed=${s} --fileout=$dcop_file
			done
		done
	done
done
