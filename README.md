# Round Robin vs SRTF – Scheduling Comparison

## Project Description

A Python desktop application that simulates and compares two CPU scheduling algorithms:
- **Round Robin (RR)** – a fairness-oriented time-slicing scheduler
- **Shortest Remaining Time First (SRTF)** – an efficiency-oriented preemptive scheduler

The application provides an interactive GUI built with Tkinter that allows users to input processes dynamically, run both algorithms simultaneously, and compare their performance through Gantt charts, results tables, and a detailed comparison summary.

---

## Requirements

- Python 3.8 or higher
- No external libraries required — uses Python's built-in `tkinter` module only

To verify Python is installed:
```bash
python --version
```

---

## Project Files

| File | Description |
|---|---|
| `gui.py` | Tkinter GUI – handles all user interaction and display |
| `algorithm.py` | Scheduling logic – Round Robin and SRTF implementations |

---

## How to Run

1. Make sure both `gui.py` and `algorithm.py` are in the **same folder**
2. Open a terminal in that folder
3. Run:

```bash
python gui.py
```

---

## Features

- Add/remove processes dynamically at runtime
- Input validation with clear error messages (including invalid quantum values)
- 5 preset test scenarios (A through E)
- Gantt chart visualization for both algorithms
- Results table showing: CT, TAT, WT, RT per process
- Average WT, TAT, and RT calculations
- Comparison summary with winner per metric
- Final conclusion with quantum effect analysis

---

## Team Members

| # | Name |
|---|---|
| 1 | يوسف محمود محمد علي |
| 2 | معاذ محمد إبراهيم حسنين |
| 3 | إسماعيل محمد عبد الحكيم نور الدين |
| 4 | كريم محمود سيد أبو طالب |
| 5 | مريم كمال يونس |
| 6 | مريم عبد العزيز عبد المعين مطراوي |
| 7 | مريم محمد عبد المنعم عبد الوهاب |

