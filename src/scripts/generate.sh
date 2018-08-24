#!/usr/bin/env bash


algorithms=("dsa" "maxsum" "ccg-maxsum" "ccg-maxsum-c" "ccg-dsa"  "dsa&ccg-maxsum" "dsa&ccg-maxsum-c" "dsa&ccg-dsa"  "dsa&rand")
cd /Users/nando/Repos/DCOP/py_dcop/

for alg in ${algorithms[@]}; do
	echo python src/py_dcop.py --algorithm=${alg} \
						        --iterations=5000 \
						        --nagents=100 \
						        --domsize=3 \
						        --seed=10 \
						        --graph="sf" \
						        --fileout='data/out/sf_s10_.csv'
done

# for alg in ${algorithms[@]}; do
# 	echo python src/py_dcop.py --algorithm=${alg} \
# 						        --iterations=5000 \
# 						        --nagents=100 \
# 						        --domsize=3 \
# 						        --seed=10 \
# 						        --graph="grid" \
# 						        --fileout='data/out/grid_s10_.csv'
# done


# for alg in ${algorithms[@]}; do
# 	echo python src/py_dcop.py --algorithm=${alg} \
# 						        --iterations=5000 \
# 						        --nagents=100 \
# 						        --domsize=3 \
# 						        --seed=10 \
# 						        --graph="rand 0.2 1.0" \
# 						        --fileout='data/out/rand_sparse_s10_.csv'
# done

# for alg in ${algorithms[@]}; do
# 	echo python src/py_dcop.py --algorithm=${alg} \
# 						        --iterations=5000 \
# 						        --nagents=100 \
# 						        --domsize=3 \
# 						        --seed=10 \
# 						        --graph="rand 0.5 1.0" \
# 						        --fileout='data/out/rand_dense_s10_.csv'
# done
