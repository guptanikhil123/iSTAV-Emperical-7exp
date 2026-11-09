# iSTAV-Emperical-7exp
iSTAV next version. This has code for 7-experiment study. Note, this uses realy openai calls

This repository contains the complete source code and raw data required to reproduce the 7-stage empirical evaluation of the iSTAV framework. 

## Repository Structure
* `/Scripts`: Contains the Python scripts for all 7 experiments (Baseline, Layer 1 Block, Layer 1 Creep, Layer 2 Mesh, Layer 4 Reset, Integrated Defense, and Full iSTAV).
* `/Results`: Contains the aggregated telemetry CSV logs and generated Matplotlib plots for structural distance (SD) and semantic drift (JD).

## Reproducibility
To run these experiments locally:
1. Ensure Docker is installed (if using the provided `docker-compose.yml` and `Dockerfile`).
2. Install dependencies: `pip install -r requirements.txt`
3. Provide your API keys via a `.env.keys` file (This file is not committed).
4. Execute the desired experiment script from the `/Scripts` directory.
