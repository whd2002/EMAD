# EMAD: AMM-Based Decentralized Energy Market

This repository contains the implementation of **EMAD**, an Automated Market Maker (AMM)-based decentralized exchange mechanism for cross-regional energy trading.

EMAD adapts the constant-product AMM mechanism, inspired by Uniswap V2, to decentralized energy markets. The system enables users to buy and sell energy across multiple regional DEXs while considering transmission losses and path feasibility.

## Overview

Traditional decentralized energy markets often suffer from fragmented liquidity, inefficient price discovery, and limited support for cross-regional trading. EMAD addresses these issues by introducing:

* AMM-based continuous liquidity provision
* Cross-pool energy trading across multiple DEXs
* Dynamic pricing based on real-time pool reserves
* Transmission-loss-aware path selection
* Blockchain-style token settlement using Energy Tokens and Money Tokens

## Main Features

* **Decentralized Energy Trading**
  Supports producers, consumers, and prosumers in a peer-to-peer energy market.

* **AMM-Based Pricing**
  Uses a constant-product formula to determine energy prices dynamically.

* **Cross-Regional Trading**
  Allows users to trade across multiple regional liquidity pools.

* **Transmission Path Optimization**
  Selects energy delivery paths while considering line losses and physical constraints.

* **Tokenized Settlement**
  Models energy and monetary flows using E-Tokens and M-Tokens.

* **Experimental Evaluation**
  Includes comparisons with baseline mechanisms such as centralized exchanges, order-book methods, single-AMM markets, and shortest-path-based approaches.

## Repository Structure

```text
EMAD/
├── data/                 # Energy market and network datasets
├── figs/                 # Figures used for analysis and visualization
├── src/                  # Core implementation
│   ├── amm.py            # AMM pricing and pool update logic
│   ├── market.py         # Energy market simulation
│   ├── network.py        # Transmission network and path modeling
│   ├── transaction.py    # Token settlement and account updates
│   └── utils.py          # Utility functions
├── experiments/          # Experimental scripts
├── results/              # Generated results and plots
├── requirements.txt      # Python dependencies
└── README.md
```

## Installation

Clone this repository:

```bash
git clone https://github.com/your-username/EMAD.git
cd EMAD
```

Create a virtual environment:

```bash
conda create -n emad python=3.9
conda activate emad
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

Run the main simulation:

```bash
python src/main.py
```

Run experiments:

```bash
python experiments/run_experiments.py
```

Generate figures:

```bash
python experiments/plot_results.py
```

## Method

EMAD models the energy market as a set of interconnected AMM-based decentralized exchanges. Each DEX maintains two reserves:

* `E-Token`: tokenized energy asset
* `M-Token`: monetary settlement asset

The AMM follows the constant-product invariant:

```text
E_LP × M_LP = K
```

When a user submits a buy order, the system evaluates candidate sellers, DEXs, and transmission paths. The optimal transaction is selected by minimizing the total effective cost, including AMM payment and transmission-related losses.

## Experimental Setup

The experiments are based on a large-scale European energy network setting, including:

* 512 users
* 37 regional DEXs
* 3,803 network nodes
* 7,072 transmission lines
* 86,016 simulated transactions
* Hourly energy trading over 7 days

The proposed mechanism is compared with multiple baseline approaches to evaluate market efficiency, price stability, user participation, and robustness under stress scenarios.

## Citation

If you use this code in your research, please cite our paper:

