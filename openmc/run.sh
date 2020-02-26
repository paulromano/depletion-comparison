#!/bin/bash

export OPENMC_CROSS_SECTIONS=$(pwd)/cross_sections.xml
export OMP_SCHEDULE=dynamic,1
nohup python run_depletion.py > stdout 2>&1 &
