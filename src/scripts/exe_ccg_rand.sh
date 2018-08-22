#!/usr/bin/env bash
prefix=$1
size=$2
rep=$3

# Paths
dcop_path="/home/fioretto/Repos/MaxSum/"
scripts_path=${dcop_path}"scripts/"

# Exe
ccg_maker=${scripts_path}"wcsp"
dcop_gen=${scripts_path}"dcop_gen_rand.py"
dcop_gen_sf=${scripts_path}"dcop_gen_scalefree.py"
dcop_gen_grid=${scripts_path}"dcop_gen_grid.py"

ccg_to_dcop=${scripts_path}"ccg_to_dcop.py"
dcop_stats=${scripts_path}"postprocess_ccg.py"
pipeline_path=${scripts_path}"code/"
ccg_solver=${pipeline_path}"wcsp-dumping"


data_path=${dcop_path}"data/$prefix/"
file_name=${prefix}_${size}_${rep}

# taskset 0x1 java -jar ${dcop_path}ccg_dcop_jar/ccg_dcop.jar ${data_path}${file}"_ccg.json" -a CCG -i ${ITERS} -o ${data_path}${file}"_stats.json"
# python $dcop_stats -i ${data_path}${file}".json" -c ${data_path}${file}"_ccg.json" -s ${data_path}${file}"_stats.json" -o out.csv
# exit

#######################
# Create instance   #Random
#######################
#out_val=$(python $dcop_gen -a ${N_AGTS} -d 2 -p ${N_P1} -r ${N_ARIETY} -c 100 -n ${N_NAME} -o ${data_path}${file})
# fail="sanity check failed!"
# if [ "$out_val" == "$fail" ]; then
#     echo "captured error $out_val"
#     exit
# fi

#######################
# Convert WCSP to CCG
#######################
echo "Converting WCSP to CCG"
start_time=$(date +%s.%N)
    $ccg_maker -K ${data_path}${file_name}".wcsp" -c ${data_path}${file_name}".ccg" > /dev/null 2>&1
    out_val=$(python $ccg_to_dcop -i ${data_path}${file_name}".ccg" -o ${data_path}${file_name}"_ccg")
    dur=$(echo "$(date +%s.%N) - $start_time" | bc)
printf "GGC computation time: %.4f seconds\n" $dur

#######################
# Solve CCG-DCOP
#######################
# java_ccg_dcop="/usr/lib/jvm/java-1.8.0-openjdk-amd64/bin/java -javaagent:/home/fioretto/Programs/intellij-2017/lib/idea_rt.jar=44460:/home/fioretto/Programs/intellij-2017/bin -Dfile.encoding=UTF-8 -classpath /usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/charsets.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/cldrdata.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/dnsns.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/icedtea-sound.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/jaccess.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/localedata.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/nashorn.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/sunec.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/sunjce_provider.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/sunpkcs11.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/zipfs.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/jce.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/jsse.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/management-agent.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/resources.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/rt.jar:/home/fioretto/Repos/MaxSum/target/classes:/home/fioretto/.m2/repository/commons-io/commons-io/2.2/commons-io-2.2.jar:/home/fioretto/.m2/repository/com/google/code/gson/gson/2.8.0/gson-2.8.0.jar:/home/fioretto/.m2/repository/com/googlecode/json-simple/json-simple/1.1.1/json-simple-1.1.1.jar:/home/fioretto/.m2/repository/junit/junit/4.10/junit-4.10.jar:/home/fioretto/.m2/repository/org/hamcrest/hamcrest-core/1.1/hamcrest-core-1.1.jar dcop_jtools"

# if [ "$out_val" == "Problem already solved" ]; then
#     echo "$out_val - skipping computation"
# else
#     echo "calling CCG DCOP solver"
#     $java_ccg_dcop ${data_path}${file_name}"_ccg.json" -a CCG -i ${ITERS} -o ${data_path}${file_name}"_stats.json"
#     #taskset 0x1 java -jar ${dcop_path}ccg_dcop_jar/ccg_dcop.jar ${data_path}${file_name}"_ccg.json" -a CCG -i ${ITERS} -o ${data_path}${file_name}"_stats.json"
#     # Compute solution
#     python $dcop_stats -i ${data_path}${file_name}".json" -c ${data_path}${file_name}"_ccg.json" -s ${data_path}${file_name}"_stats.json" -o out.csv
# fi

#exit

#######################
# Solve c++
#######################
echo "wcsp with BP on original problem "
start_time=$(date +%s.%N)
    $ccg_solver -M -t 600 ${data_path}${file_name}.wcsp
    dur=$(echo "$(date +%s.%N) - $start_time" | bc)
printf "%.2f seconds\n" $dur

# echo "wcsp with BP on CCG problem + Kernelization "
# start_time=$(date +%s.%N)
#     $ccg_solver -m m -t 600 ${data_path}${file_name}.wcsp
#     dur=$(echo "$(date +%s.%N) - $start_time" | bc)
# printf "%.2f seconds\n" $dur

# echo "wcsp with BP on CCG problem  (No KERNELIZATION) "
# start_time=$(date +%s.%N)
#     $ccg_solver -m m -k -t 600 ${data_path}${file_name}.wcsp
#     dur=$(echo "$(date +%s.%N) - $start_time" | bc)
# printf "%.2f seconds\n" $dur

echo "DCOP on CCG with Kernelization: "
start_time=$(date +%s.%N)
    $ccg_solver -m d -t 600 ${data_path}${file_name}.wcsp
    dur=$(echo "$(date +%s.%N) - $start_time" | bc)
printf "%.2f seconds\n" $dur

echo "DCOP on CCG NO Kernelization: "
start_time=$(date +%s.%N)
    $ccg_solver -m d -k -t 600 ${data_path}${file_name}.wcsp
    dur=$(echo "$(date +%s.%N) - $start_time" | bc)
printf "%.2f seconds\n" $dur

# echo "wcsp with LP: "
# start_time=$(date +%s.%N)
#     $ccg_solver -m l -t 600 ${data_path}${file_name}.wcsp | egrep "value|best"
#     dur=$(echo "$(date +%s.%N) - $start_time" | bc)
# printf "%.2f seconds\n" $dur


#######################
# Solve MaxSum
#######################
# echo "MaxSum (FRODO) on original graph "

# start_time=$(date +%s.%N)
#     taskset 0x1 ${pipeline_path}maxSumPipeline.sh ${data_path}${file_name}
#     dur=$(echo "$(date +%s.%N) - $start_time" | bc)
# printf "%.2f seconds\n" $dur

#echo "MaxSum (FRODO) on CCG "
#
#start_time=$(date +%s.%N)
#    taskset 0x1 ${pipeline_path}maxSumPipeline.sh ${data_path}${file_name}"_ccg_dcop"
#    dur=$(echo "$(date +%s.%N) - $start_time" | bc)
#printf "%.2f seconds\n" $dur


#######################
# Solve DSA
#######################
echo "DSA (FRODO)"

start_time=$(date +%s.%N)
    taskset 0x1 ${pipeline_path}dsaPipeline.sh ${data_path}${file_name}
    dur=$(echo "$(date +%s.%N) - $start_time" | bc)
printf "%.2f seconds\n" $dur


#echo "DSA (FRODO) on CCG"
#
#start_time=$(date +%s.%N)
#    taskset 0x1 ${pipeline_path}dsaPipeline.sh ${data_path}${file_name}"_ccg_dcop"
#    dur=$(echo "$(date +%s.%N) - $start_time" | bc)
#printf "%.2f seconds\n" $dur
#
