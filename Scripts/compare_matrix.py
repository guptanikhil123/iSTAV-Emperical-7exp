import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import os

# Configuration
results_dir = "results/"
output_file = "istav_comparative_matrix_2x2_advanced.png"
L1_CEIL = 0.50
COL_JD = 'JD'

def load_exp(exp_id):
    try:
        df = pd.read_csv(f"{results_dir}telemetry_exp{exp_id}.csv")
        iter_col = 'Iteration' if 'Iteration' in df.columns else 'iteration'
        
        # Handle legacy column names for backward compatibility
        if 'Format Drift' in df.columns:
            df.rename(columns={'Format Drift': 'SD'}, inplace=True)
        elif 'DoM' in df.columns:
            df.rename(columns={'DoM': 'SD'}, inplace=True)
            
        struct_col = 'SD' if 'SD' in df.columns else 'SD'
            
        # Include Tau_eff in the grouped mean calculations
        df_mean = df.groupby(iter_col)[[struct_col, COL_JD, 'Tau_eff']].mean(numeric_only=True).reset_index()
        df_mean = df_mean.sort_values(by=iter_col)
        return df_mean, iter_col, struct_col
    except FileNotFoundError:
        print(f"Warning: Data for Exp {exp_id} not found.")
        return pd.DataFrame(), 'Iteration', 'SD'

# Set up the 2x2 grid
fig, axs = plt.subplots(2, 2, figsize=(16, 12))
# Adjust 'top' to leave room for the global legend
plt.subplots_adjust(hspace=0.25, wspace=0.15, top=0.90) 

# Load the relevant experiments
df1, it1, st1 = load_exp(1)
df2, it2, st2 = load_exp(2)
df3, it3, st3 = load_exp(3)
df6, it6, st6 = load_exp(6)
df7, it7, st7 = load_exp(7)

# --- Standardized Styles for the Matrix ---
style_ref_sd  = {'color': 'royalblue', 'marker': 'o', 'linestyle': '-'}
style_ref_jd  = {'color': 'crimson', 'marker': 's', 'linestyle': '-'}
style_ref_tau = {'color': 'mediumseagreen', 'linestyle': '-.', 'linewidth': 1.5}

style_cmp_sd  = {'color': 'teal', 'marker': '^', 'linestyle': '--'}
style_cmp_jd  = {'color': 'purple', 'marker': 'd', 'linestyle': '--'}
style_cmp_tau = {'color': 'mediumseagreen', 'linestyle': '-', 'linewidth': 2.5}

# --- Panel (a): Perimeter Defense (Exp 1 vs 2) ---
ax = axs[0, 0]
if not df1.empty and not df2.empty:
    ax.plot(df1[it1], df1[st1], **style_ref_sd)
    ax.plot(df1[it1], df1[COL_JD], **style_ref_jd)
    ax.plot(df1[it1], df1['Tau_eff'], **style_ref_tau)
    ax.plot(df2[it2], df2[st2], **style_cmp_sd)
    ax.plot(df2[it2], df2[COL_JD], **style_cmp_jd)
    ax.plot(df2[it2], df2['Tau_eff'], **style_cmp_tau)
ax.set_title('(a) Perimeter Defense: Baseline vs L1 Block (Exp 1 vs 2)', fontweight='bold')

# --- Panel (b): The Evasion Gap (Exp 2 vs 3) ---
ax = axs[0, 1]
if not df2.empty and not df3.empty:
    ax.plot(df2[it2], df2[st2], **style_ref_sd)
    ax.plot(df2[it2], df2[COL_JD], **style_ref_jd)
    ax.plot(df2[it2], df2['Tau_eff'], **style_ref_tau)
    ax.plot(df3[it3], df3[st3], **style_cmp_sd)
    ax.plot(df3[it3], df3[COL_JD], **style_cmp_jd)
    ax.plot(df3[it3], df3['Tau_eff'], **style_cmp_tau)
ax.set_title('(b) The Evasion Gap: L1 Block vs L1 Creep (Exp 2 vs 3)', fontweight='bold')

# --- Panel (c): Cognitive Recovery (Exp 3 vs 6) ---
ax = axs[1, 0]
if not df3.empty and not df6.empty:
    ax.plot(df3[it3], df3[st3], **style_ref_sd)
    ax.plot(df3[it3], df3[COL_JD], **style_ref_jd)
    ax.plot(df3[it3], df3['Tau_eff'], **style_ref_tau)
    ax.plot(df6[it6], df6[st6], **style_cmp_sd)
    ax.plot(df6[it6], df6[COL_JD], **style_cmp_jd)
    ax.plot(df6[it6], df6['Tau_eff'], **style_cmp_tau)
ax.set_title('(c) Cognitive Recovery: L1 Creep vs Integrated Defense (Exp 3 vs 6)', fontweight='bold')

# --- Panel (d): Systemic Capstone (Exp 1 vs 7) ---
ax = axs[1, 1]
if not df1.empty and not df7.empty:
    ax.plot(df1[it1], df1[st1], **style_ref_sd)
    ax.plot(df1[it1], df1[COL_JD], **style_ref_jd)
    ax.plot(df1[it1], df1['Tau_eff'], **style_ref_tau)
    ax.plot(df7[it7], df7[st7], **style_cmp_sd)
    ax.plot(df7[it7], df7[COL_JD], **style_cmp_jd)
    ax.plot(df7[it7], df7['Tau_eff'], **style_cmp_tau)
ax.set_title('(d) Framework Efficacy: Baseline vs Full iSTAV (Exp 1 vs 7)', fontweight='bold')

# --- Formatting for all subplots ---
for ax in axs.flat:
    ax.axhline(y=L1_CEIL, color='black', linestyle=':')
    ax.axvline(x=5, color='orange', linestyle='--', alpha=0.7)
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Distance Metric / Trust Margin')
    ax.set_ylim([-0.05, 1.1])
    ax.set_xlim([1, 16])
    # Individual legends are intentionally removed

# --- Global Unified Legend ---
legend_handles = [
    mlines.Line2D([], [], **style_ref_sd, label='SD (Reference)'),
    mlines.Line2D([], [], **style_ref_jd, label='JD (Reference)'),
    mlines.Line2D([], [], **style_ref_tau, label=r'$\tau_{eff}$ (Reference)'),
    mlines.Line2D([], [], color='black', linestyle=':', label=r'$L1_{ceil}$ (0.50)'),
    
    mlines.Line2D([], [], **style_cmp_sd, label='SD (Intervention)'),
    mlines.Line2D([], [], **style_cmp_jd, label='JD (Intervention)'),
    mlines.Line2D([], [], **style_cmp_tau, label=r'$\tau_{eff}$ (Intervention)'),
    mlines.Line2D([], [], color='orange', linestyle='--', alpha=0.7, label='Injection starts')
]

fig.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=4, fontsize='large', frameon=True, edgecolor='black')

# Save the figure
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Matrix successfully generated and saved to {output_file}")