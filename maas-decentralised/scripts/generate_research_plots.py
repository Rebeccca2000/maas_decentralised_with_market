#!/usr/bin/env python3
"""
Robust Research Plots Generator for Decentralized MaaS.
Fixes: Explicit mode mapping, robust duration handling, accurate secondary market detection.
"""
import argparse
import glob
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# === Configuration ===
plt.style.use("seaborn-v0_8-paper")
sns.set_context("paper", font_scale=1.4)
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.dpi": 300,
})

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "artifacts" / "paper_visuals"

def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def latest_file(pattern: str) -> Path | None:
    files = list(Path(".").glob(pattern)) + list(REPO_ROOT.glob(pattern))
    return max(files, key=os.path.getmtime) if files else None

# === 1. Robust Mode Classification ===
def get_mode_category(raw_mode):
    """Maps raw provider types to clean categories for plotting."""
    m = str(raw_mode).lower().strip()
    
    if "train" in m: return "Train"
    if "bus" in m: return "Bus"
    if "bike" in m: return "Bike"
    if "car" in m or "uber" in m or "taxi" in m: return "Car"
    if "bundle" in m: return "Bundle"
    
    return "Unknown" # Explicitly track errors

# === Plot: Active Mode Share Evolution (Lines) ===
def plot_mode_share_evolution(bookings_csv: Path):
    print(f"📊 Generating Robust Mode Share Evolution from {bookings_csv.name}...")
    try:
        df = pd.read_csv(bookings_csv)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    if df.empty: return

    # Filter out speculator/system bookings (keep real commuters only)
    if "commuter_id" in df.columns:
        before = len(df)
        df = df[df["commuter_id"] < 1000]  # adjust threshold if needed
        removed = before - len(df)
        if removed > 0:
            print(f"🧹 Filtered out {removed} non-commuter bookings (commuter_id >= 1000).")

    # 1. Normalize Modes
    if "mode_category" in df.columns:
        df["clean_mode"] = df["mode_category"].apply(get_mode_category)
    else:
        df["clean_mode"] = df["mode"].apply(get_mode_category)
    # Treat unknown as bundle for visualization (avoids missing series)
    df["clean_mode"] = df["clean_mode"].replace({"Unknown": "Bundle"})

    # 2. Handle Duration & Timing
    # Fallback if columns missing
    if "start_tick" not in df.columns: df["start_tick"] = df.get("tick", 0)
    if "duration" not in df.columns: df["duration"] = 1 # Default to 1 tick duration
    
    # Force numeric and handle NaNs
    df["start_tick"] = pd.to_numeric(df["start_tick"], errors='coerce').fillna(0).astype(int)
    df["duration"] = pd.to_numeric(df["duration"], errors='coerce').fillna(1).astype(int)
    
    # Ensure minimum duration of 1 for visibility
    df["duration"] = df["duration"].clip(lower=1)
    
    df["end_tick"] = df["start_tick"] + df["duration"]
    
    max_tick = int(df["end_tick"].max()) + 5
    
    # 3. Build Timeline Matrix
    modes = ["Train", "Bus", "Car", "Bike", "Bundle"]
    colors = ["#d62728", "#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
    
    timeline = {m: np.zeros(max_tick) for m in modes}

    for _, row in df.iterrows():
        mode = row["clean_mode"]
        if mode not in timeline: mode = "Unknown"
        
        start = row["start_tick"]
        end = min(row["end_tick"], max_tick)
        
        # Increment counter for every tick this trip is active
        timeline[mode][start:end] += 1

    # 4. Plot as lines (no filled areas)
    x = np.arange(max_tick)
    fig, ax = plt.subplots(figsize=(12, 6))
    for m, c in zip(modes, colors):
        series = pd.Series(timeline[m])
        smooth = series.rolling(window=10, min_periods=1, center=True).mean()
        ax.plot(x, smooth.values, label=m, color=c, linewidth=2)
    ax.set_title("Real-time Active Trips by Mode (Line View)", fontweight="bold")
    ax.set_xlabel("Simulation Tick")
    ax.set_ylabel("Number of Active Trips")
    ax.legend(loc="upper left")
    ax.set_xlim(0, max_tick)
    # Peak hour shading
    ax.axvspan(30, 60, color="gray", alpha=0.1, label="Peak Hour")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "mode_share_evolution_robust.png")
    plt.close()
    print(f"✅ Saved to {OUTPUT_DIR / 'mode_share_evolution_robust.png'}")

# === Plot: Price Stratification ===
def plot_price_stratification(bookings_csv: Path):
    print(f"📈 Generating Robust Price Stratification from {bookings_csv.name}...")
    df = pd.read_csv(bookings_csv)
    if df.empty: return

    # Filter out speculator/system bookings (keep real commuters only)
    if "commuter_id" in df.columns:
        before = len(df)
        df = df[df["commuter_id"] < 1000]
        removed = before - len(df)
        if removed > 0:
            print(f"🧹 Filtered out {removed} non-commuter bookings (commuter_id >= 1000).")

    # 1. Strict Classification (No Price Guessing)
    def classify(row):
        src = str(row.get("source", "")).lower()
        if "secondary" in src or "nft_market" in src:
            return "Secondary (Scalper)"
        return "Primary (Provider)"

    df["market_type"] = df.apply(classify, axis=1)
    df["clean_mode"] = df["mode"].apply(get_mode_category)

    # 2. Add Jitter
    df["tick_jitter"] = df["tick"] + np.random.uniform(-0.5, 0.5, len(df))
    df["price_jitter"] = df["price"] + np.random.uniform(-0.1, 0.1, len(df))

    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Define markers/colors
    palette = {"Primary (Provider)": "#1f77b4", "Secondary (Scalper)": "#d62728"}
    # Include Bundle to avoid missing marker errors when style column has Bundle
    markers = {"Train": "s", "Bus": "o", "Car": "^", "Bike": "v", "Bundle": "X", "Unknown": "D"}

    sns.scatterplot(
        data=df, x="tick_jitter", y="price_jitter",
        hue="market_type", style="clean_mode",
        palette=palette, markers=markers,
        s=60, alpha=0.7, ax=ax
    )

    ax.set_title("Market Price Discovery: Primary vs Secondary", fontweight="bold")
    ax.set_xlabel("Simulation Tick")
    ax.set_ylabel("Transaction Price ($)")
    
    # Dynamic Base Lines (Optional: Draw if needed, but avoid hardcoding values if they changed)
    # ax.axhline(12.0, color='gray', linestyle=':', alpha=0.5, label="Train Base")
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "price_stratification_robust.png")
    plt.close()
    print(f"✅ Saved to {OUTPUT_DIR / 'price_stratification_robust.png'}")

# === Main ===
def main():
    ensure_output_dir()
    bookings_path = latest_file("bookings_*.csv")
    
    if bookings_path:
        plot_mode_share_evolution(bookings_path)
        plot_price_stratification(bookings_path)
    else:
        print("❌ No bookings CSV found.")

if __name__ == "__main__":
    main()
