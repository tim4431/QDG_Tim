#!/bin/bash
#SBATCH --job-name=spins
#SBATCH --account=fc_qudev
#SBATCH --partition=savio3
#SBATCH --time=30:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=20
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=xinwei@berkeley.edu
#
## Command(s) to run:
echo "hello world"
module load python
# cd ~/Tim/spins-b
# make install
# echo "installation complete"
cd ~/Tim/QDG_Tim/230907_spins/3_grating_straight_w1326_released_1
# echo $cwd
# nohup python3 grating.py run ./output > grating.log 2>&1 &
python3 grating.py run ./output
python3 grating.py view ./output
echo "end of job"
