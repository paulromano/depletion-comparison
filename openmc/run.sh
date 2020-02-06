#!/bin/bash

export OPENMC_CROSS_SECTIONS=$(pwd)/cross_sections.xml
nohup python run_depletion.py > stdout 2>&1 &
