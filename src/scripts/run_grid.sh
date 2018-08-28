#!/usr/bin/env bash

algorithms=("dsa" "maxsum" "ccg-maxsum+" "ccg-maxsum+k" "ccg-maxsum" "ccg-maxsum-c"
            "ccg-dsa"  "dsa&ccg-maxsum" "dsa&ccg-maxsum-c" "dsa&ccg-dsa"  "dsa&rand")

#py_dcop_home="/home/fioretto/Repos/py_dcop"
py_dcop_home="/Users/nando/Repos/DCOP/py_dcop"
cd ${py_dcop_home}

seeds=(1) # 20 30 40 50 60 70 80 90 100)
for seed in ${seeds[@]}; do    
	dcop_file="${py_dcop_home}/data/in/grid_${seed}.json"
	python src/py_dcop2.py --nagents=20 --domsize=3 --seed=${seed} --graph="grid" --fileout="${dcop_file}"
	
	for alg in ${algorithms[@]}; do
	    echo "grid " $alg " seed " $seed
	 	python src/py_dcop2.py --algorithm="${alg}" \
	 	       --iterations=1000 \
	 	       --seed=${seed} \
	 	       --filein="${dcop_file}" \
	 	       --fileout="${py_dcop_home}/data/out/${alg}_grid_s${seed}_.csv"
	done

done
