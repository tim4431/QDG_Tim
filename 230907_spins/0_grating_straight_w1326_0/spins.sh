#!/bin/bash
#SBATCH --job-name=spins
#SBATCH --account=fc_qudev
#SBATCH --partition=savio3
#SBATCH --time=20:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=xinwei@berkeley.edu
#
## Command(s) to run:
echo "hello world"
module load python
# cd ~/Tim/spins-b
# make install
# echo "installation complete"
cd ~/Tim/QDG_Tim/230907_spins/0_grating_straight_w1326_0
# echo $cwd
# nohup python3 grating.py run ./output > grating.log 2>&1 &
python3 grating.py run ./output
python3 grating.py view ./output
echo "end of job"
