# Mars Tycoon: Sol Survival

Mars Tycoon: Sol Survival is a strategy resource management game where you play as the Mission Commander of the first permanent Martian settlement. Your goal is to balance critical life-support systems, manage a fragile economy, and research the technology needed to terraform Mars—all while surviving the harsh realities of the Red Planet.

## Gameplay Features

- **Base Building**: Construct Solar Arrays, Data Centers, O2 Scrubbers, and Hab Modules. Every building consumes energy and land, requiring careful planning.
- **Resource Management:** Balance Energy, Oxygen, Population, and Cash.
    - *Running out of Energy triggers blackouts.*
    - *Running out of Oxygen kills colonists.*
    - *Running out of Cash halts expansion.*
- **Real-Time Crypto Economy:** Your Data Centers mine crypto to fund the colony. The revenue depends on the real-world live price of Bitcoin (BTC) (via Yahoo Finance API).
- **Tech Tree:** Unlock advanced technologies like Perovskite Cells (Solar Boost), Quantum ASICs (Mining Boost), and Nuclear Reactors (Weather-proof power) to reach the ultimate goal: Terraforming.
- **Workforce Allocation:** Assign your population as Engineers (to boost grid efficiency) or Scientists (to boost compute yields).
- **Simulation Engine:** Survive random equipment failures, blackouts, and colony accidents.

## Getting Started

### Prerequisites

You need Python 3.8+ installed. You will also need the Graphviz system binaries for the tech tree visualization.

### Installation

1.  **Install dependencies:**
    ```bash
    pip install streamlit pandas numpy plotly yfinance graphviz
    ```

    *> **Note:** If you get a "Graphviz Executable Not Found" error, you need to install Graphviz on your system (e.g., `brew install graphviz` on Mac or download the installer for Windows).*

2.  **Run the game:**
    ```bash
    streamlit run mars_tycoon_sol.py
    ```

3.  **Play:** The game will automatically open in your web browser at `http://localhost:8501`.

## How to Play

1.  **The HUD:** Monitor your resources at the top. Keep Oxygen and Energy positive!
2.  **Build:** Go to the `BASE` tab to expand your infrastructure.
    * *Tip: Build Solar Arrays early to support your power grid.*
3.  **Research:** Use the `RESEARCH` tab to unlock upgrades. You cannot win without the Terraforming tech.
4.  **Operate:** Use the `OPERATIONS` tab to assign workers and execute turns.
    * **Sleep (1 Sol):** Advances time by 1 day.
    * **Skip Week (7 Sols):** Fast forwards time (risky if your resources are unstable!).
5.  **Win Condition:** Research the "Terraforming" technology to win the game.
6.  **Lose Condition:** If your Population reaches 0, the colony fails.

---
