
import tkinter as tk
from tkinter import ttk, messagebox
import statistics

from algorithm import (
    round_robin, srtf_preemptive,
    validate_quantum, validate_processes,
    SCENARIOS,
)

# Colours 
BG      = "#f0f0f0"
WHITE   = "#ffffff"
BLUE    = "#2563eb"
RED     = "#dc2626"
GREEN   = "#16a34a"
GRAY    = "#6b7280"
DARK    = "#111827"

GANTT_COLORS = [
    "#3b82f6","#ef4444","#22c55e","#f59e0b",
    "#8b5cf6","#ec4899","#14b8a6","#f97316",
]

FONT  = ("Arial", 10)
FONTB = ("Arial", 10, "bold")
FONTT = ("Arial", 13, "bold")
FONTM = ("Courier", 10)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Round Robin vs SRTF")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.process_rows = []   

        self._build()
        self._load_scenario("A – Basic Mixed Workload")

    
    # Build UI
    
    def _build(self):
        # Title 
        tk.Label(self, text="Round Robin vs SRTF ",
                 font=FONTT, bg=BLUE, fg=WHITE,
                 pady=8).pack(fill="x")

        # Input 
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=10, pady=8)
        self._build_input(top)

        # Notebook 
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tab_rr  = tk.Frame(nb, bg=BG)
        tab_sf  = tk.Frame(nb, bg=BG)
        tab_cmp = tk.Frame(nb, bg=BG)

        nb.add(tab_rr,  text="  Round Robin  ")
        nb.add(tab_sf,  text="     SRTF      ")
        nb.add(tab_cmp, text="  Comparison & Conclusion  ")

        self._build_algo_tab(tab_rr, "rr")
        self._build_algo_tab(tab_sf, "srtf")
        self._build_comparison(tab_cmp)

    #  Input section 

    def _build_input(self, parent):
        box = tk.LabelFrame(parent, text="Input", font=FONTB,
                            bg=BG, padx=8, pady=6)
        box.pack(side="left", anchor="se", fill="y")

        # Scenario
        tk.Label(box, text="Preset Scenario:", font=FONT, bg=BG).grid(
            row=0, column=0, columnspan=3, sticky="w")
        self.scenario_var = tk.StringVar()
        cb = ttk.Combobox(box, textvariable=self.scenario_var,
                          values=list(SCENARIOS.keys()),
                          state="readonly", font=FONT, width=30)
        cb.grid(row=1, column=0, columnspan=3, pady=(0, 8), sticky="w")
        cb.bind("<<ComboboxSelected>>",
                lambda e: self._load_scenario(self.scenario_var.get()))

        # Quantum
        tk.Label(box, text="Time Quantum:", font=FONT, bg=BG).grid(
            row=2, column=0, sticky="w")
        self.q_var = tk.StringVar(value="3")
        tk.Entry(box, textvariable=self.q_var, font=FONT,
                 width=6, relief="solid").grid(row=2, column=1, sticky="w", padx=4)

        
        self.rows_frame = tk.Frame(box, bg=BG)
        self.rows_frame.grid(row=3, column=0, columnspan=3, sticky="w", pady=(10, 0))

        
        self.rows_frame.columnconfigure(0, minsize=60)
        self.rows_frame.columnconfigure(1, minsize=80)
        self.rows_frame.columnconfigure(2, minsize=80)

        
        tk.Label(self.rows_frame, text="PID",     font=FONTB, bg=BG, anchor="center").grid(row=0, column=0, padx=2, pady=(0,2), sticky="ew")
        tk.Label(self.rows_frame, text="Arrival", font=FONTB, bg=BG, anchor="center").grid(row=0, column=1, padx=2, pady=(0,2), sticky="ew")
        tk.Label(self.rows_frame, text="Burst",   font=FONTB, bg=BG, anchor="center").grid(row=0, column=2, padx=2, pady=(0,2), sticky="ew")

        # Buttons
        btn_frame = tk.Frame(box, bg=BG)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=8, sticky="w")

        tk.Button(btn_frame, text="+ Add Process",
                  command=self._add_row,
                  bg=BLUE, fg=WHITE, font=FONT, relief="flat",
                  padx=8, pady=3).pack(side="left", padx=(0,4))

        tk.Button(btn_frame, text="▶ Run",
                  command=self._run,
                  bg=GREEN, fg=WHITE, font=FONT, relief="flat",
                  padx=8, pady=3).pack(side="left", padx=(0,4))

        tk.Button(btn_frame, text="Clear",
                  command=self._clear,
                  bg=RED, fg=WHITE, font=FONT, relief="flat",
                  padx=8, pady=3).pack(side="left")

        # Ready queue
        rq_box = tk.LabelFrame(parent, text="RR Ready Queue (initial order)",
                               font=FONTB, bg=BG, padx=8, pady=6)
        rq_box.pack(side="left", anchor="n", padx=(12,0), fill="y")

        self.rq_lbl = tk.Label(rq_box, text="—", font=FONTM,
                               bg=BG, fg=BLUE, justify="left")
        self.rq_lbl.pack(anchor="w")

    #  Algo tab 

    def _build_algo_tab(self, parent, key):
        title = "Round Robin" if key == "rr" else "SRTF"

        # Gantt
        tk.Label(parent, text=f"{title} – Gantt Chart",
                 font=FONTB, bg=BG).pack(anchor="w", padx=10, pady=(10, 2))
        canvas = tk.Canvas(parent, bg=WHITE, height=65, width=700,
                           highlightthickness=1, highlightbackground=GRAY)
        canvas.pack(padx=10, pady=(0, 8))
        setattr(self, f"gantt_{key}", canvas)

        # Table
        tk.Label(parent, text=f"{title} – Results Table",
                 font=FONTB, bg=BG).pack(anchor="w", padx=10, pady=(4, 2))
        
        cols = ("PID", "Arrival", "Burst", "CT", "TAT", "WT", "RT")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=7)
        

        style = ttk.Style()
        style.configure("Treeview",         font=FONT, rowheight=22)
        style.configure("Treeview.Heading", font=FONTB)

        widths = {"PID":50,"Arrival":65,"Burst":60,"CT":55,"TAT":60,"WT":55,"RT":55}
        for c in cols:
            tree.heading(c, text=c)
            
            tree.column(c, width=widths[c], anchor="center")

        tree.pack(padx=10)
        setattr(self, f"tree_{key}", tree)

        avg_lbl = tk.Label(parent, text="", font=FONTM, bg=BG, fg=DARK)
        avg_lbl.pack(anchor="w", padx=12, pady=(4, 0))
        setattr(self, f"avg_{key}", avg_lbl)

    # Comparison & Conclusion 

    def _build_comparison(self, parent):
        tk.Label(parent, text="Comparison Summary",
                 font=FONTB, bg=BG).pack(anchor="w", padx=10, pady=(10, 2))

        self.cmp_lbl = tk.Label(parent,
                                text="Run the simulation to see the comparison.",
                                font=FONTM, bg=WHITE, fg=DARK,
                                justify="left", anchor="nw",
                                relief="solid", padx=10, pady=8)
        self.cmp_lbl.pack(fill="x", padx=10)

        tk.Label(parent, text="Conclusion",
                 font=FONTB, bg=BG).pack(anchor="w", padx=10, pady=(12, 2))

        self.conc_lbl = tk.Label(parent, text="—",
                                 font=FONTM, bg="#fffbeb", fg="#92400e",
                                 justify="left", anchor="nw",
                                 relief="solid", padx=10, pady=8)
        self.conc_lbl.pack(fill="x", padx=10, pady=(0, 10))

    
    # Process row management
        
    def _add_row(self, pid="", arrival="", burst=""):
       
        row_num = len(self.process_rows) + 1

        pv = tk.StringVar(value=pid)
        av = tk.StringVar(value=arrival)
        bv = tk.StringVar(value=burst)

        
        e_pid = tk.Entry(self.rows_frame, textvariable=pv, font=FONT, width=6,  relief="solid", justify="center")
        e_arr = tk.Entry(self.rows_frame, textvariable=av, font=FONT, width=8,  relief="solid", justify="center")
        e_bur = tk.Entry(self.rows_frame, textvariable=bv, font=FONT, width=8,  relief="solid", justify="center")

        e_pid.grid(row=row_num, column=0, padx=2, pady=2, sticky="ew")
        e_arr.grid(row=row_num, column=1, padx=2, pady=2, sticky="ew")
        e_bur.grid(row=row_num, column=2, padx=2, pady=2, sticky="ew")

        entry = [pv, av, bv, e_pid, e_arr, e_bur, None]
        del_btn = tk.Button(
            self.rows_frame, text="✕", font=FONT, bg=RED, fg=WHITE,
            relief="flat", padx=4,
            command=lambda e=entry: self._del_row(e)
        )
        del_btn.grid(row=row_num, column=3, padx=2, pady=2)
        entry[6] = del_btn

        self.process_rows.append(entry)

    def _del_row(self, entry):
        if entry in self.process_rows:
            self.process_rows.remove(entry)
        pv, av, bv, e_pid, e_arr, e_bur, del_btn = entry
        e_pid.destroy()
        e_arr.destroy()
        e_bur.destroy()
        del_btn.destroy()

    def _clear(self):
        for pv, av, bv, e_pid, e_arr, e_bur, del_btn in self.process_rows:
            e_pid.destroy()
            e_arr.destroy()
            e_bur.destroy()
            del_btn.destroy()
        self.process_rows.clear()
        self.gantt_rr.delete("all")
        self.gantt_srtf.delete("all")
        self.tree_rr.delete(*self.tree_rr.get_children())
        self.tree_srtf.delete(*self.tree_srtf.get_children())
        self.avg_rr.config(text="")
        self.avg_srtf.config(text="")
        self.rq_lbl.config(text="—")
        self.cmp_lbl.config(text="Run the simulation to see the comparison.")
        self.conc_lbl.config(text="—")

    
    # Load scenario
    

    def _load_scenario(self, name):
        if name not in SCENARIOS:
            return
        s = SCENARIOS[name]
        self._clear()
        for pid, arr, burst in s["processes"]:
            self._add_row(pid, arr, burst)
        self.q_var.set(s["quantum"])
        self.scenario_var.set(name)

    
    # Run
    

    def _run(self):
        raw = [(pv.get(), av.get(), bv.get()) for pv, av, bv, *_ in self.process_rows]

        try:
            rr_list, srtf_list = validate_processes(raw)
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        try:
            q = validate_quantum(self.q_var.get())
        except ValueError as e:
            messagebox.showerror("Invalid Quantum", str(e))
            return

        rr_comp,   rr_gantt   = round_robin(rr_list, q)
        srtf_comp, srtf_gantt = srtf_preemptive(srtf_list)

        self._draw_gantt(self.gantt_rr,   rr_gantt)
        self._draw_gantt(self.gantt_srtf, srtf_gantt)

        self._fill_table(self.tree_rr,   self.avg_rr,   rr_comp,   rr_list,   "rr")
        self._fill_table(self.tree_srtf, self.avg_srtf, srtf_comp, srtf_list, "srtf")

        self._show_rq(rr_list, q)
        self._show_comparison(rr_comp, srtf_comp, q)

    
    # Rendering
    

    def _draw_gantt(self, canvas, gantt):
        canvas.delete("all")
        if not gantt:
            return

        slots = []
        t = 0
        for entry in gantt:
            if slots and slots[-1][0] == entry:
                slots[-1][2] += 1
            else:
                slots.append([entry, t, t + 1])
            t += 1

        unique = sorted(list(dict.fromkeys(s[0] for s in slots if s[0] != "Idle")))
        color_map = {pid: GANTT_COLORS[i % len(GANTT_COLORS)] for i, pid in enumerate(unique)}
        color_map["Idle"] = "#d1d5db"

        max_t  = slots[-1][2]
        W      = 680
        scale  = W / max(max_t, 1)
        BAR_Y  = 8
        BAR_H  = 30

        for pid, start, end in slots:
            x0 = 10 + start * scale
            x1 = 10 + end   * scale
            canvas.create_rectangle(x0, BAR_Y, x1, BAR_Y + BAR_H,
                                    fill=color_map.get(pid, GRAY),
                                    outline=WHITE, width=1)
            canvas.create_text((x0 + x1) / 2, BAR_Y + BAR_H / 2,
                                text=pid, fill=WHITE, font=("Arial", 9, "bold"))
            canvas.create_text(x0, BAR_Y + BAR_H + 10,
                                text=str(start), fill=GRAY, font=("Arial", 8))

        canvas.create_text(10 + max_t * scale, BAR_Y + BAR_H + 10,
                           text=str(max_t), fill=GRAY, font=("Arial", 8))

    def _fill_table(self, tree, avg_lbl, completed, proc_list, algo):
        tree.delete(*tree.get_children())

        info = ({p[2]: (p[0], p[1]) for p in proc_list} if algo == "rr"
                else {p[2]: (p[1], p[0]) for p in proc_list})

        wts, tats, rts = [], [], []
        for pid in sorted(completed.keys()):
            ct, tat, wt, rt = completed[pid]
            arrival, burst = info[pid]
            tree.insert("", "end", values=(pid, arrival, burst, ct, tat, wt, rt))
            wts.append(wt); tats.append(tat); rts.append(rt)

        n = len(wts)
        if n:
            avg_lbl.config(
                text=(f"Avg WT: {sum(wts)/n:.2f}   "
                      f"Avg TAT: {sum(tats)/n:.2f}   "
                      f"Avg RT: {sum(rts)/n:.2f}"))

    def _show_rq(self, rr_list, q):
        ordered = sorted(rr_list, key=lambda p: (p[0], p[2]))
        self.rq_lbl.config(
            text="  →  ".join(p[2] for p in ordered) + f"\nQuantum = {q}")

    def _show_comparison(self, rr_comp, srtf_comp, q):
        def avg(d, idx): return sum(v[idx] for v in d.values()) / len(d)

        rr_wt  = avg(rr_comp,   2);  sf_wt  = avg(srtf_comp, 2)
        rr_tat = avg(rr_comp,   1);  sf_tat = avg(srtf_comp, 1)
        rr_rt  = avg(rr_comp,   3);  sf_rt  = avg(srtf_comp, 3)
        rr_std = statistics.pstdev([v[2] for v in rr_comp.values()])
        sf_std = statistics.pstdev([v[2] for v in srtf_comp.values()])

        def w(a, b): return "RR WINS" if a < b else ("SRTF WINS" if b < a else "Tie")

        lines = [
            f"Avg WT   :  RR={rr_wt:.2f}   SRTF={sf_wt:.2f}   →  {w(rr_wt, sf_wt)}",
            f"Avg TAT  :  RR={rr_tat:.2f}  SRTF={sf_tat:.2f}  →  {w(rr_tat, sf_tat)}",
            f"Avg RT   :  RR={rr_rt:.2f}   SRTF={sf_rt:.2f}   →  {w(rr_rt, sf_rt)}",
            f"Fairness :  WT std-dev  RR={rr_std:.2f}  SRTF={sf_std:.2f}   →  {'RR fairer ' if rr_std <= sf_std else 'SRTF fairer WINS'}",
            f"Quantum  :  Q={q}  →  {'Small: frequent preemptions, low RT' if q<=2 else 'Medium: balanced' if q<=5 else 'Large: behaves like FCFS'}",
        ]

        self.cmp_lbl.config(text="\n".join(lines))

        sf_WINSs = sum([sf_wt < rr_wt, sf_tat < rr_tat, sf_rt < rr_rt])
        rr_WINSs = sum([rr_wt < sf_wt, rr_tat < sf_tat, rr_rt < sf_rt])
        if sf_WINSs > rr_WINSs:
            verdict = (f"► SRTF is more efficient (won {sf_WINSs}/3 metrics).\n"
                       f"  Better average WT and TAT — favors short jobs.\n"
                       f"  Recommended for CPU-bound workloads.")
        elif rr_WINSs > sf_WINSs:
            verdict = (f"► Round Robin is more balanced (won {rr_WINSs}/3 metrics).\n"
                       f"  Fairer distribution of CPU time across all processes.\n"
                       f"  Recommended for interactive workloads.")
        else:
            verdict = ("► Both algorithms performed equally on measured metrics.\n"
                       "  Choose Round Robin for fairness, SRTF for efficiency.")

        q_note = ("Small quantum → many preemptions, low response time, high overhead." if q <= 2
                  else "Medium quantum → balanced preemption and throughput." if q <= 5
                  else "Large quantum → few preemptions, Round Robin behaves like FCFS.")

        self.conc_lbl.config(text=f"{verdict}\n\nQuantum effect (Q={q}): {q_note}")


#  Entry point 

if __name__ == "__main__":
    app = App()
    app.mainloop()