import matplotlib.pyplot as plt
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv(".env")
RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
EXPERIMENT_ID = os.getenv("EXPERIMENT_ID", "1")
filepath = os.path.join(RESULTS_DIR, f"telemetry_exp{EXPERIMENT_ID}.csv")

def generate_plot():
    if not os.path.exists(filepath):
        print(f"No telemetry file found at {filepath}")
        return

    df = pd.read_csv(filepath)
    iter_col = 'Iteration' if 'Iteration' in df.columns else 'iteration'
    
    # Backward compatibility mapping for old CSV headers
    if 'Format Drift' in df.columns:
        df.rename(columns={'Format Drift': 'SD'}, inplace=True)
    if 'DoM' in df.columns:
        df.rename(columns={'DoM': 'SD'}, inplace=True)
    if 'Xi_eff' in df.columns:
        df.rename(columns={'Xi_eff': 'Tau_eff'}, inplace=True)
        
    if 'SD' not in df.columns:
        return
        
    df_grouped = df.groupby(iter_col)
    df_mean = df_grouped.mean(numeric_only=True).reset_index()
    df_std = df_grouped.std(numeric_only=True).fillna(0).reset_index()

    raw_title = os.environ.get("PLOT_TITLE", f"Experiment {EXPERIMENT_ID} Telemetry")
    PLOT_TITLE = raw_title.split(" (Run")[0]

    SHIFT_ITERATION = int(os.environ.get("SHIFT_ITERATION", "5"))
    L1_CEIL = float(os.environ.get("L1_CEIL", "0.50"))
    TAU_FLOOR = float(os.environ.get("TAU_FLOOR", "0.90"))
    L4_FLOOR = float(os.environ.get("L4_FLOOR", "0.10"))

    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Plot primary metrics
    ax1.plot(df_mean[iter_col], df_mean['SD'], label='SD', color='mediumblue', marker='o', zorder=5)
    ax1.fill_between(df_mean[iter_col], (df_mean['SD'] - df_std['SD']).clip(lower=0), df_mean['SD'] + df_std['SD'], color='blue', alpha=0.15)
    
    ax1.plot(df_mean[iter_col], df_mean['JD'], label='JD', color='firebrick', marker='s', zorder=5)
    ax1.fill_between(df_mean[iter_col], (df_mean['JD'] - df_std['JD']).clip(lower=0), df_mean['JD'] + df_std['JD'], color='red', alpha=0.15)
    
    ax1.plot(df_mean[iter_col], df_mean['Tau_eff'], label=r'$\tau_{eff}$', color='darkgreen', linestyle='-.', zorder=5)
    ax1.fill_between(df_mean[iter_col], (df_mean['Tau_eff'] - df_std['Tau_eff']).clip(lower=0), (df_mean['Tau_eff'] + df_std['Tau_eff']).clip(upper=1), color='green', alpha=0.1)

    # Plot Dynamic Thresholds
    ax1.axhline(y=TAU_FLOOR, color='firebrick', linestyle='--', alpha=0.5, label=r'$\tau_{floor}$', zorder=4)
    ax1.axhline(y=L1_CEIL, color='darkblue', linestyle='--', alpha=0.8, label=r'$L1_{ceil}$', zorder=4)
    ax1.axhline(y=L4_FLOOR, color='crimson', linestyle=':', alpha=0.8, label=r'$L4_{floor}$', zorder=4)

    # Axis config
    max_iter = df_mean[iter_col].max()
    ax1.set_xlim(1, max_iter)
    ax1.margins(x=0)
    ax1.set_xlabel('Iteration', fontsize=12)
    ax1.set_ylabel('Distance / Trust Margin', color='black', fontsize=12)
    ax1.set_ylim(-0.05, 1.2)
    ax1.set_xticks(range(1, int(max_iter) + 1))
    
    if SHIFT_ITERATION <= max_iter:
        ax1.axvline(x=SHIFT_ITERATION, color='goldenrod', linestyle='--', label='Injection Starts', zorder=3)
        ax1.text(SHIFT_ITERATION + 0.1, 0.45, r'Injection Starts $\downarrow$', color='goldenrod', fontsize=10, rotation=90, va='top', ha='left')
    
    n_runs = df['run_id'].nunique() if 'run_id' in df.columns else 1
    
    # 1. Data-Driven L1 Block Detection 
    blocks = df[df['Action'] == 'BLOCKED']
    if not blocks.empty:
        block_counts = blocks.groupby(iter_col).size()
        ax1.scatter([], [], color='mediumblue', marker='x', s=150, linewidth=2, label='L1 Block')
        ax1.scatter([], [], color='red', marker='v', s=150, label='L4 Reset')
        
        for x_val, count in block_counts.items():
            if count >= (n_runs * 0.5): 
                ax1.scatter(x_val, 0.0, color='mediumblue', marker='x', s=150, linewidth=2, zorder=10)
                ax1.annotate(f"{count}", (x_val, 0.025), color='mediumblue', fontsize=10, ha='center', va='bottom')
            elif count >= (n_runs * 0.25): 
                ax1.annotate(f"{count}", (x_val, 0.025), color='steelblue', fontsize=10, alpha=0.8, ha='center', va='bottom')

    # 2. Data-Driven L4 Reset Detection 
    if 'Tau_eff' in df.columns:
        reset_counts = {}
        for run_id, group in df.groupby('run_id'):
            group = group.sort_values(iter_col)
            for i in range(1, len(group)):
                prev_x = group.iloc[i-1]['Tau_eff']
                curr_x = group.iloc[i]['Tau_eff']
                if prev_x <= L4_FLOOR + 0.05 and curr_x >= 0.95:
                    iter_val = group.iloc[i][iter_col]
                    reset_counts[iter_val] = reset_counts.get(iter_val, 0) + 1
                    break 
        
        for x_val, count in reset_counts.items():
            if count >= (n_runs * 0.5): 
                ax1.scatter(x_val, 0.0, color='crimson', marker='v', s=150, zorder=10)
                ax1.annotate(f"{count}", (x_val, 0.06), color='crimson', fontsize=10, ha='center', va='bottom')
            elif count >= (n_runs * 0.25): 
                ax1.annotate(f"{count}", (x_val, 0.06), color='indianred', fontsize=10, alpha=0.8, ha='center', va='bottom')

    plt.title(f"{PLOT_TITLE} (Aggregated N={n_runs})", fontsize=14)
    ax1.legend(loc='upper left', fontsize=10, ncol=4)
    plt.tight_layout()
    out_path = f"exp{EXPERIMENT_ID}_aggregated_plot.png"
    plt.savefig(out_path)

if __name__ == "__main__":
    generate_plot()