#!/usr/bin/env bash


algorithms=("dsa" "maxsum" "ccg-maxsum" "ccg-maxsum-c" "ccg-dsa"  "dsa&ccg-maxsum" "dsa&ccg-maxsum-c" "dsa&ccg-dsa"  "dsa&rand")
cd /home/fioretto/Repos/py_dcop/

seeds=(10 20 30 40 50 60 70 80 90 100)
for seed in ${seeds[@]}; do
 #    for alg in ${algorithms[@]}; do
	# 	echo "sf " $alg " seed " $seed
	# 	python src/py_dcop.py --algorithm=${alg} \
	# 	       --iterations=5000 \
	# 	       --nagents=100 \
	# 	       --domsize=3 \
	# 	       --seed=${seed} \
	# 	       --graph="sf" \
	# 	       --fileout="data/out/${alg}_sf_s${seed}_.csv"
 #    done
    
 #    for alg in ${algorithms[@]}; do
	# echo "grid " $alg " seed " $seed
	# 	python src/py_dcop.py --algorithm=${alg} \
	# 	       --iterations=5000 \
	# 	       --nagents=100 \
	# 	       --domsize=3 \
	# 	       --seed=${seed} \
	# 	       --graph="grid" \
	# 	       --fileout="data/out/${alg}_grid_s${seed}_.csv"
 #    done
    
 #    for alg in ${algorithms[@]}; do
	# echo "rand sparse " $alg " seed " $seed
	# 	python src/py_dcop.py --algorithm=${alg} \
	# 	       --iterations=5000 \
	# 	       --nagents=100 \
	# 	       --domsize=3 \
	# 	       --seed=${seed} \
	# 	       --graph="rand-sparse" \
	# 	       --fileout="data/out/${alg}_rand_sparse_s${seed}_.csv"
 #    done
    
    for alg in ${algorithms[@]}; do
	echo "rand dense " $alg " seed " $seed
		python src/py_dcop.py --algorithm=${alg} \
		       --iterations=5000 \
		       --nagents=100 \
		       --domsize=3 \
		       --seed=${seed} \
		       --graph="rand-dense" \
		       --fileout="data/out/${alg}_rand_dense_s${seed}_.csv"
    done
done
