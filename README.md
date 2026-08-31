# 🛡️ ASGARD V24 - Numerical Relativity & GRMHD Simulator

**Asgard V24** is a high-performance, hybrid CPU/GPU simulator for Numerical Relativity and General Relativistic Magnetohydrodynamics (GRMHD). It implements the full BSSN 3+1 formalism with dynamic gauges, ideal GRMHD with GLM divergence cleaning, and relativistic ray-tracing for black hole shadow imaging.

[![Python 3.10+](https://shields.io)](https://python.org)
[![License: MIT](https://shields.io)](https://opensource.org)
[![CI](https://github.com)](https://github.com)

---

## 🌟 Key Features

- **BSSN 3+1 Formalism**: Full hyperbolic evolution of Einstein's field equations.
- **Dynamic Gauges**: 1+log slicing for the lapse function ($\alpha$) and hyperbolic Gamma-Driver for the shift vector ($\beta^i$).
- **GRMHD Core**: Ideal magnetohydrodynamics with GLM divergence cleaning (Dedner filter) to maintain $\nabla_i B^i = 0$.
- **Relativistic Ray-Tracing**: Real-time null-geodesic solver to render black hole shadows and ergosphere light deflection.
- **Poynting Extraction**: Quantitative power measurement of the Blandford-Znajek mechanism to calculate energy extraction.
- **Hybrid Backend**: Auto-detecting execution environment via NumPy/CuPy (CPU/GPU) with vector optimization.
- **HDF5 Checkpoints**: High-performance scientific persistence with integrated gzip compression for massive simulations.

---

## 📐 Mathematical Formulation

The total energy-momentum tensor incorporates relativistic perfect fluids and magnetic fields:

$$T_{\mu\nu} = \left(\rho_0 h + b^2\right) u_\mu u_\nu + \left(P + \frac{1}{2}b^2\right) g_{\mu\nu} - b_\mu b_\nu$$

The magnetic fields are evolved and swept by frame-dragging using the coordinate shift vector $\beta^i$:

$$\partial_t B^i = \partial_j \left( \beta^j B^i - \beta^i B^j \right) + \partial_j \left( \alpha \gamma^{jk} \epsilon_{kmn} v^m B^n \right)$$

---

## 📊 Validation & Verification

| Test Suite | Metric Measured | Target/Analytical | Scientific Status |
| :--- | :--- | :--- | :--- |
| **Schwarzschild Static** | Gauge Stability ($\alpha$, $\chi$) | $\text{std}(\alpha) < 10^{-4}$ | ✅ Verified |
| **Teukolsky GW** | Propagation Velocity ($v_g$) | $v \approx c$ (error < 4.5%) | ✅ Verified |
| **Frame-Dragging** | Lense-Thirring Profile ($\beta^i$) | Analytical Kerr vs Mesh | ✅ Verified |
| **GLM Divergence** | Monopole Control ($\psi$) | $\psi < 10^{-12}$ decay | ✅ Verified |
| **Convergence Order** | Truncation Error ($p$) | $p \approx 4.0$ (Richardson) | ✅ Verified |

---

## 📁 Repository Structure

```yaml
asgard_v24/
│
├── .github/workflows/ci.yml   # Continuous Integration Pipeline
├── asgard/                    # Main Numerical Core Package
│   ├── __init__.py
│   ├── config.py              # Physics & Execution Constants
│   ├── core_geometry.py       # Spacetime Mesh and Positions
│   ├── core_matter.py         # Relativistic Fluids and GRMHD T_munu
│   ├── bssn_maxwell_clean.py  # 3+1 Evolution and GLM Filter
│   ├── poynting_extractor.py  # Energy Extraction Analytics
│   └── ray_tracer.py          # Relativistic Ray-Tracing Engine
│
├── tests/                     # Scientific Verification Suite
│   ├── test_grmhd_rigor.py
│   ├── test_schwarzschild_static.py
│   └── analysis_richardson.py
│
├── run_asgard_v24_production.py # Master Pipeline Orchestrator
├── README.md
├── LICENSE                    # MIT License
└── requirements.txt           # Dependency Stack
```

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com
cd asgard_v24

# Install standard dependencies
pip install -r requirements.txt

# Run the complete production pipeline (Validates & Simulates)
python run_asgard_v24_production.py
```

To install with full **NVIDIA CUDA GPU** hardware acceleration:
```bash
pip install .[gpu]
```

---

## 📖 Citation

If you utilize Asgard V24 in your academic research, please cite this work as follows:

```bibtex
@article{asgard_v24_2026,
    author = {Yenderson Guevara and DeepSeek AI, and Gemini AI},
    title = {Asgard V24: A Hybrid CPU/GPU Simulator for Numerical Relativity and GRMHD},
    journal = {GitHub Software Repository},
    year = {2026},
    url = {https://github.com}
}
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

---

## 👤 Author

**Yenderson Guevara**
* GitHub: [@13narut-creator](https://github.com)
* Research Focus: Numerical Relativity, GRMHD, and High-Performance Scientific Computing.
