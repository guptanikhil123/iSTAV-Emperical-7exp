#!/bin/bash
# plot_only.sh - Regenerate plots without re-running the swarm
# Usage: ./plot_only.sh <EXPERIMENT_ID>

EXPERIMENT_ID=$1

if [[ ! "$EXPERIMENT_ID" =~ ^[1-7]$ ]]; then
    echo "Error: Please specify an experiment number (1-7)."
    exit 1
fi

RESULTS_DIR="results"
TELEMETRY_FILE="$RESULTS_DIR/telemetry_exp${EXPERIMENT_ID}.csv"
rm -f "./exp${EXPERIMENT_ID}_aggregated_plot.png"

if [ ! -f "$TELEMETRY_FILE" ]; then
    echo "Error: File $TELEMETRY_FILE does not exist. Run the experiment first."
    exit 1
fi

case "$EXPERIMENT_ID" in
    1) TITLE="Experiment 1: Baseline" ;;
    2) TITLE="Experiment 2: L2 Block" ;;
    3) TITLE="Experiment 3: L2 Creep" ;;
    4) TITLE="Experiment 4: L3 Mesh" ;;
    5) TITLE="Experiment 5: L4 Reset" ;;
    6) TITLE="Experiment 6: L4 Defense" ;;
    7) TITLE="Experiment 7: Full iSTAV" ;;
esac

echo "Regenerating plot for $TITLE from $TELEMETRY_FILE..."
docker run --rm   -v "$PWD:/app"   -w /app   -e RESULTS_DIR="$RESULTS_DIR"   -e EXPERIMENT_ID="$EXPERIMENT_ID"   -e PLOT_TITLE="$TITLE"   python:3.10-slim   sh -c "pip install pandas matplotlib python-dotenv > /dev/null 2>&1 && python plot.py"
echo "Done."
