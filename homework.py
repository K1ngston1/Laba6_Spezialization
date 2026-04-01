import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import re

def calculate_specialization_index(nm_base, noo, noa):
    if nm_base == 0:
        return 0, "Invalid (NM_base cannot be zero)"
    si = (noo + noa) / nm_base
    status = "Aggressive Inheritance" if si > 0.5 else "Stable"
    return si, status

def calculate_ck_metrics(wmc, dit, cbo, lcom, rfc, thresholds):
    return [wmc > thresholds['WMC'], dit > thresholds['DIT'],
            cbo > thresholds['CBO'], lcom > thresholds['LCOM'],
            rfc > thresholds['RFC']]

def calculate_mood(total_methods, hidden_methods, total_attrs, hidden_attrs, coupling_factor, poly_factor):
    mhf = (hidden_methods / total_methods * 100) if total_methods > 0 else 0
    ahf = (hidden_attrs / total_attrs * 100) if total_attrs > 0 else 0
    cof = coupling_factor * 100
    pof = poly_factor * 100
    return ahf, mhf, cof, pof

def calculate_ucp(actors_simple, actors_avg, actors_complex,
                  uc_simple, uc_avg, uc_complex,
                  tcf, ecf, hours_per_ucp=20):
    actor_weights = {'simple': 1, 'average': 2, 'complex': 3}
    uc_weights = {'simple': 5, 'average': 10, 'complex': 15}
    uaw = (actors_simple * actor_weights['simple'] +
           actors_avg * actor_weights['average'] +
           actors_complex * actor_weights['complex'])
    uucw = (uc_simple * uc_weights['simple'] +
            uc_avg * uc_weights['average'] +
            uc_complex * uc_weights['complex'])
    uucp = uaw + uucw
    ucp = uucp * tcf * ecf
    hours = ucp * hours_per_ucp
    return ucp, hours

def calculate_pert(optimistic, most_likely, pessimistic):
    expected = (optimistic + 4 * most_likely + pessimistic) / 6
    sd = (pessimistic - optimistic) / 6
    safe_deadline = expected + 2 * sd
    return expected, sd, safe_deadline

class VariantData:
    """Central storage for all variant data."""
    def __init__(self):

        self.data = {
            "SmartClinic": (

                (5, 3, 1, 2, 1, 1, 3, "Very High"),

                (2, 1, 2, 5, 3, 1, 0.95, 0.85),

                (45, 60, 90)
            ),
            "AeroCheck": (
                (8, 4, 2, 4, 2, 1, 5, "Low"),
                (4, 3, 1, 8, 4, 2, 1.10, 1.05),
                (60, 85, 150)
            ),
            "EcoLogistics": (
                (4, 2, 0, 2, 1, 0, 2, "High"),
                (1, 2, 1, 4, 2, 1, 0.80, 0.90),
                (30, 40, 70)
            ),
            "FoodDash": (
                (12, 6, 3, 6, 3, 2, 8, "Very Low"),
                (5, 4, 3, 12, 6, 4, 1.05, 1.15),
                (90, 120, 210)
            ),
            "EduPortal": (
                (6, 3, 1, 3, 2, 0, 4, "Very High"),
                (2, 2, 1, 6, 3, 1, 0.90, 0.80),
                (40, 55, 80)
            ),
            "BankGuard": (
                (10, 5, 4, 5, 4, 3, 10, "High"),
                (10, 5, 2, 10, 5, 4, 1.20, 0.75),
                (70, 100, 180)
            ),
            "FitTrack Pro": (
                (4, 2, 1, 2, 1, 1, 2, "Low"),
                (1, 1, 2, 4, 2, 1, 0.85, 0.95),
                (25, 35, 60)
            ),
            "AutoPart Finder": (
                (7, 4, 1, 4, 2, 1, 5, "High"),
                (3, 2, 1, 7, 4, 1, 0.95, 1.00),
                (50, 65, 110)
            ),
            "GreenEnergy Grid": (
                (9, 3, 2, 3, 2, 2, 6, "Very High"),
                (6, 3, 1, 9, 3, 2, 1.15, 0.85),
                (55, 75, 130)
            ),
            "CinemaBooking": (
                (5, 2, 1, 2, 1, 0, 3, "Extra High"),
                (1, 1, 1, 5, 2, 1, 0.75, 0.90),
                (20, 30, 55)
            ),
            "PetHotel": (
                (6, 3, 0, 3, 2, 0, 3, "High"),
                (2, 1, 1, 6, 3, 1, 0.85, 1.00),
                (35, 45, 75)
            ),
            "Warehouse360": (
                (11, 5, 3, 5, 3, 2, 9, "Very Low"),
                (8, 4, 2, 11, 5, 3, 1.05, 1.10),
                (80, 110, 190)
            ),
            "CryptoWallet": (
                (8, 4, 5, 4, 3, 4, 12, "Very High"),
                (12, 5, 3, 8, 4, 5, 1.25, 0.80),
                (65, 90, 160)
            ),
            "RealEstate Scan": (
                (7, 3, 1, 3, 2, 1, 4, "High"),
                (2, 2, 2, 7, 3, 1, 0.90, 0.95),
                (45, 55, 100)
            ),
            "SmartHome Hub": (
                (10, 6, 2, 5, 4, 1, 7, "High"),
                (10, 6, 2, 10, 6, 2, 1.10, 0.85),
                (75, 95, 165)
            ),
            "EventMaster": (
                (5, 4, 1, 2, 2, 1, 3, "Low"),
                (2, 1, 1, 5, 4, 1, 0.80, 1.05),
                (30, 42, 85)
            ),
            "SteamCloud Shop": (
                (15, 8, 4, 8, 5, 3, 15, "Very Low"),
                (15, 8, 4, 15, 8, 4, 1.15, 1.10),
                (100, 140, 250)
            ),
            "LawCase Manager": (
                (6, 3, 2, 3, 2, 1, 4, "Very High"),
                (1, 2, 2, 6, 3, 2, 0.95, 0.90),
                (40, 60, 110)
            ),
            "TaxiRide Core": (
                (9, 4, 1, 4, 3, 1, 6, "High"),
                (4, 3, 2, 9, 4, 1, 1.00, 1.05),
                (50, 70, 120)
            ),
            "LibraryNext": (
                (4, 2, 0, 2, 1, 0, 2, "Extra High"),
                (1, 1, 1, 4, 2, 0, 0.70, 0.95),
                (25, 32, 55)
            )
        }

    def get_system_names(self):
        return list(self.data.keys())

    def get_composition(self, system):
        return self.data[system][0]

    def get_ucp(self, system):
        return self.data[system][1]

    def get_pert(self, system):
        return self.data[system][2]

variant_data = VariantData()

class HierarchyAnalyzerFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Hierarchy Analyzer (Specialization Index)", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="NM_base (Methods in Base Class):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.nm_base = ttk.Entry(self, width=15)
        self.nm_base.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(self, text="NOO (Overridden Methods):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.noo = ttk.Entry(self, width=15)
        self.noo.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(self, text="NOA (Added Methods):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.noa = ttk.Entry(self, width=15)
        self.noa.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(self, text="L (Depth of Inheritance):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.l = ttk.Entry(self, width=15)
        self.l.grid(row=4, column=1, padx=5, pady=2)
        self.l.insert(0, "0")

        ttk.Button(self, text="Calculate SI", command=self.calculate).grid(row=5, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(self, text="", font=("Arial", 10))
        self.result_label.grid(row=6, column=0, columnspan=2, pady=5)

    def calculate(self):
        try:
            nm_base = float(self.nm_base.get())
            noo = float(self.noo.get())
            noa = float(self.noa.get())
            if nm_base == 0:
                messagebox.showerror("Error", "NM_base cannot be zero.")
                return
            si, status = calculate_specialization_index(nm_base, noo, noa)
            self.result_label.config(text=f"SI = {si:.2f} → {status}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")

class CKMetricsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.thresholds = {'WMC': 40, 'DIT': 5, 'CBO': 15, 'LCOM': 0.5, 'RFC': 50}

    def create_widgets(self):
        ttk.Label(self, text="CK Metrics Dashboard", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        self.metrics = {}
        row = 1
        for metric in ['WMC', 'DIT', 'CBO', 'LCOM', 'RFC']:
            ttk.Label(self, text=f"{metric}:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            entry = ttk.Entry(self, width=15)
            entry.grid(row=row, column=1, padx=5, pady=2)
            self.metrics[metric] = entry
            row += 1

        ttk.Button(self, text="Evaluate", command=self.evaluate).grid(row=row, column=0, columnspan=2, pady=10)

        self.results_frame = ttk.Frame(self)
        self.results_frame.grid(row=row+1, column=0, columnspan=2, pady=5)

    def evaluate(self):
        try:
            values = {}
            for metric, entry in self.metrics.items():
                val = float(entry.get())
                values[metric] = val

            flags = calculate_ck_metrics(values['WMC'], values['DIT'], values['CBO'],
                                         values['LCOM'], values['RFC'], self.thresholds)

            for widget in self.results_frame.winfo_children():
                widget.destroy()

            for i, (metric, val) in enumerate(values.items()):
                color = "red" if flags[i] else "black"
                label = ttk.Label(self.results_frame, text=f"{metric}: {val}", foreground=color)
                label.grid(row=i, column=0, sticky=tk.W, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Please enter numeric values for all metrics.")

class MOODAnalyzerFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="MOOD Analyzer", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Total Methods:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_methods = ttk.Entry(self, width=15)
        self.total_methods.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(self, text="Hidden Methods:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.hidden_methods = ttk.Entry(self, width=15)
        self.hidden_methods.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(self, text="Total Attributes:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_attrs = ttk.Entry(self, width=15)
        self.total_attrs.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(self, text="Hidden Attributes:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.hidden_attrs = ttk.Entry(self, width=15)
        self.hidden_attrs.grid(row=4, column=1, padx=5, pady=2)

        ttk.Label(self, text="Coupling Factor (0-1):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.coupling_factor = ttk.Entry(self, width=15)
        self.coupling_factor.grid(row=5, column=1, padx=5, pady=2)

        ttk.Label(self, text="Polymorphism Factor (0-1):").grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.poly_factor = ttk.Entry(self, width=15)
        self.poly_factor.grid(row=6, column=1, padx=5, pady=2)

        ttk.Button(self, text="Calculate MOOD", command=self.calculate).grid(row=7, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(self, text="", font=("Arial", 10))
        self.result_label.grid(row=8, column=0, columnspan=2)

    def calculate(self):
        try:
            total_m = float(self.total_methods.get())
            hidden_m = float(self.hidden_methods.get())
            total_a = float(self.total_attrs.get())
            hidden_a = float(self.hidden_attrs.get())
            cf = float(self.coupling_factor.get())
            pf = float(self.poly_factor.get())

            ahf, mhf, cof, pof = calculate_mood(total_m, hidden_m, total_a, hidden_a, cf, pf)
            self.result_label.config(text=f"AHF: {ahf:.2f}% | MHF: {mhf:.2f}% | COF: {cof:.2f}% | POF: {pof:.2f}%")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")

class UCPCalculatorFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="UCP Calculator", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=6, pady=10)

        ttk.Label(self, text="Select System (optional):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.ucp_system_var = tk.StringVar()
        self.ucp_system_combo = ttk.Combobox(self, textvariable=self.ucp_system_var, values=variant_data.get_system_names(), width=20)
        self.ucp_system_combo.grid(row=1, column=1, padx=5)
        ttk.Button(self, text="Load Variant Data", command=self.load_ucp_variant).grid(row=1, column=2, padx=5)

        ttk.Label(self, text="Actors (Simple):").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.actors_simple = ttk.Entry(self, width=10)
        self.actors_simple.grid(row=2, column=1, padx=5)
        ttk.Label(self, text="Avg:").grid(row=2, column=2, sticky=tk.W)
        self.actors_avg = ttk.Entry(self, width=10)
        self.actors_avg.grid(row=2, column=3, padx=5)
        ttk.Label(self, text="Complex:").grid(row=2, column=4, sticky=tk.W)
        self.actors_complex = ttk.Entry(self, width=10)
        self.actors_complex.grid(row=2, column=5, padx=5)

        ttk.Label(self, text="Use Cases (Simple):").grid(row=3, column=0, sticky=tk.W, padx=5)
        self.uc_simple = ttk.Entry(self, width=10)
        self.uc_simple.grid(row=3, column=1, padx=5)
        ttk.Label(self, text="Avg:").grid(row=3, column=2, sticky=tk.W)
        self.uc_avg = ttk.Entry(self, width=10)
        self.uc_avg.grid(row=3, column=3, padx=5)
        ttk.Label(self, text="Complex:").grid(row=3, column=4, sticky=tk.W)
        self.uc_complex = ttk.Entry(self, width=10)
        self.uc_complex.grid(row=3, column=5, padx=5)

        ttk.Label(self, text="TCF (Technical Complexity Factor):").grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5)
        self.tcf = ttk.Entry(self, width=10)
        self.tcf.grid(row=4, column=2, padx=5, sticky=tk.W)
        ttk.Label(self, text="ECF (Environmental Complexity Factor):").grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5)
        self.ecf = ttk.Entry(self, width=10)
        self.ecf.grid(row=5, column=2, padx=5, sticky=tk.W)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=6, column=0, columnspan=6, pady=10)
        self.result_label = ttk.Label(self, text="", font=("Arial", 10))
        self.result_label.grid(row=7, column=0, columnspan=6)

    def load_ucp_variant(self):
        system = self.ucp_system_var.get()
        if not system:
            return
        ucp_data = variant_data.get_ucp(system)
        self.actors_simple.delete(0, tk.END)
        self.actors_simple.insert(0, str(ucp_data[0]))
        self.actors_avg.delete(0, tk.END)
        self.actors_avg.insert(0, str(ucp_data[1]))
        self.actors_complex.delete(0, tk.END)
        self.actors_complex.insert(0, str(ucp_data[2]))
        self.uc_simple.delete(0, tk.END)
        self.uc_simple.insert(0, str(ucp_data[3]))
        self.uc_avg.delete(0, tk.END)
        self.uc_avg.insert(0, str(ucp_data[4]))
        self.uc_complex.delete(0, tk.END)
        self.uc_complex.insert(0, str(ucp_data[5]))
        self.tcf.delete(0, tk.END)
        self.tcf.insert(0, str(ucp_data[6]))
        self.ecf.delete(0, tk.END)
        self.ecf.insert(0, str(ucp_data[7]))

    def calculate(self):
        try:
            actors_s = int(self.actors_simple.get() or 0)
            actors_a = int(self.actors_avg.get() or 0)
            actors_c = int(self.actors_complex.get() or 0)
            uc_s = int(self.uc_simple.get() or 0)
            uc_a = int(self.uc_avg.get() or 0)
            uc_c = int(self.uc_complex.get() or 0)
            tcf = float(self.tcf.get())
            ecf = float(self.ecf.get())

            ucp, hours = calculate_ucp(actors_s, actors_a, actors_c, uc_s, uc_a, uc_c, tcf, ecf)
            self.result_label.config(text=f"UCP = {ucp:.2f}\nEstimated Person-Hours = {hours:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")

class PERTRiskEngineFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.fig, self.ax = plt.subplots(figsize=(4, 2))
        self.canvas = None

    def create_widgets(self):
        ttk.Label(self, text="PERT Risk Engine", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Select System (optional):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.pert_system_var = tk.StringVar()
        self.pert_system_combo = ttk.Combobox(self, textvariable=self.pert_system_var, values=variant_data.get_system_names(), width=20)
        self.pert_system_combo.grid(row=1, column=1, padx=5)
        ttk.Button(self, text="Load Variant Data", command=self.load_pert_variant).grid(row=1, column=2, padx=5)

        ttk.Label(self, text="Optimistic (O):").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.optimistic = ttk.Entry(self, width=10)
        self.optimistic.grid(row=2, column=1, padx=5)

        ttk.Label(self, text="Most Likely (M):").grid(row=3, column=0, sticky=tk.W, padx=5)
        self.most_likely = ttk.Entry(self, width=10)
        self.most_likely.grid(row=3, column=1, padx=5)

        ttk.Label(self, text="Pessimistic (P):").grid(row=4, column=0, sticky=tk.W, padx=5)
        self.pessimistic = ttk.Entry(self, width=10)
        self.pessimistic.grid(row=4, column=1, padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=5, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(self, text="", font=("Arial", 10))
        self.result_label.grid(row=6, column=0, columnspan=2)

        self.graph_frame = ttk.Frame(self)
        self.graph_frame.grid(row=7, column=0, columnspan=2, pady=10)

    def load_pert_variant(self):
        system = self.pert_system_var.get()
        if not system:
            return
        pert_data = variant_data.get_pert(system)  # (o, m, p)
        self.optimistic.delete(0, tk.END)
        self.optimistic.insert(0, str(pert_data[0]))
        self.most_likely.delete(0, tk.END)
        self.most_likely.insert(0, str(pert_data[1]))
        self.pessimistic.delete(0, tk.END)
        self.pessimistic.insert(0, str(pert_data[2]))

    def calculate(self):
        try:
            o = float(self.optimistic.get())
            m = float(self.most_likely.get())
            p = float(self.pessimistic.get())

            exp, sd, safe = calculate_pert(o, m, p)

            self.result_label.config(text=f"Expected Time (E): {exp:.2f}\nStd Dev: {sd:.2f}\nSafe Deadline (E+2SD): {safe:.2f}")

            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            self.ax.clear()
            labels = ['O', 'M', 'P']
            values = [o, m, p]
            colors = ['green', 'yellow', 'red']
            self.ax.bar(labels, values, color=colors)
            self.ax.axhline(y=exp, color='blue', linestyle='--', label=f'E={exp:.1f}')
            self.ax.axhline(y=safe, color='orange', linestyle='--', label=f'Safe={safe:.1f}')
            self.ax.legend()
            self.ax.set_title("PERT Estimates")
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack()
        except ValueError:
            messagebox.showerror("Error", "Please enter numeric values.")

class CommercialProposalFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.app = None

    def create_widgets(self):
        ttk.Label(self, text="Commercial Proposal Generator", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Total Person-Hours:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.hours = ttk.Entry(self, width=15)
        self.hours.grid(row=1, column=1, padx=5)

        ttk.Label(self, text="Risk Reserve (%) :").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.risk_reserve = ttk.Entry(self, width=15)
        self.risk_reserve.insert(0, "15")
        self.risk_reserve.grid(row=2, column=1, padx=5)

        ttk.Button(self, text="Generate Proposal", command=self.generate).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Fetch from UCP & PERT", command=self.fetch_data).grid(row=4, column=0, columnspan=2, pady=5)

        self.result_text = tk.Text(self, height=12, width=50)
        self.result_text.grid(row=5, column=0, columnspan=2, pady=10)

    def fetch_data(self):
        if self.app is None:
            messagebox.showerror("Error", "Application reference not set.")
            return
        ucp_frame = self.app.ucp_frame
        pert_frame = self.app.pert_frame
        if ucp_frame is None or pert_frame is None:
            messagebox.showinfo("Info", "Please ensure you have calculated results in UCP and PERT frames first.")
            return

        ucp_result = ucp_frame.result_label.cget("text")
        match = re.search(r"Estimated Person-Hours = ([\d\.]+)", ucp_result)
        if match:
            hours = float(match.group(1))
            self.hours.delete(0, tk.END)
            self.hours.insert(0, f"{hours:.2f}")
        else:
            messagebox.showwarning("Warning", "Could not parse UCP result. Please calculate UCP first.")
            return

        pert_result = pert_frame.result_label.cget("text")
        match = re.search(r"Std Dev: ([\d\.]+)", pert_result)
        if match:
            sd = float(match.group(1))
            match_exp = re.search(r"Expected Time \(E\): ([\d\.]+)", pert_result)
            if match_exp:
                exp = float(match_exp.group(1))
                buffer_hours = 2 * sd * 8
                buffer_pct = (buffer_hours / hours) * 100 if hours > 0 else 0
                self.risk_reserve.delete(0, tk.END)
                self.risk_reserve.insert(0, f"{buffer_pct:.0f}")
                messagebox.showinfo("Info", f"Suggested risk reserve: {buffer_pct:.0f}% (based on PERT SD)")
            else:
                messagebox.showwarning("Warning", "Could not parse PERT expected time.")
        else:
            messagebox.showwarning("Warning", "Could not parse PERT standard deviation. Please calculate PERT first.")

    def generate(self):
        try:
            hours = float(self.hours.get())
            reserve_pct = float(self.risk_reserve.get())
            rate = 35.0
            development_cost = hours * rate
            reserve = development_cost * (reserve_pct / 100)
            total = development_cost + reserve

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Development Hours: {hours:.2f}\n")
            self.result_text.insert(tk.END, f"Hourly Rate: ${rate:.2f}\n")
            self.result_text.insert(tk.END, f"Development Cost: ${development_cost:.2f}\n")
            self.result_text.insert(tk.END, f"Risk Reserve ({reserve_pct:.0f}%): ${reserve:.2f}\n")
            self.result_text.insert(tk.END, f"Total Proposal: ${total:.2f}\n")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")

class ConceptualDesignFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Conceptual Design (Step 1)", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="System Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.system_name = ttk.Entry(self, width=40)
        self.system_name.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(self, text="System Description:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.system_desc = tk.Text(self, height=3, width=40)
        self.system_desc.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(self, text="Scenarios (NSS - 3 scenarios):", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.scenarios = []
        for i in range(3):
            lbl = ttk.Label(self, text=f"Scenario {i+1}:")
            lbl.grid(row=4+i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = ttk.Entry(self, width=60)
            entry.grid(row=4+i, column=1, padx=5, pady=2)
            self.scenarios.append(entry)

        ttk.Label(self, text="Key Classes (NKC - 5 classes):", font=("Arial", 10, "bold")).grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.key_classes = []
        for i in range(5):
            lbl = ttk.Label(self, text=f"Class {i+1}:")
            lbl.grid(row=8+i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = ttk.Entry(self, width=40)
            entry.grid(row=8+i, column=1, padx=5, pady=2)
            self.key_classes.append(entry)

        ttk.Label(self, text="Subsystems (NSU - 2-3 subsystems):", font=("Arial", 10, "bold")).grid(row=13, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.subsystems = []
        for i in range(3):
            lbl = ttk.Label(self, text=f"Subsystem {i+1}:")
            lbl.grid(row=14+i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = ttk.Entry(self, width=40)
            entry.grid(row=14+i, column=1, padx=5, pady=2)
            self.subsystems.append(entry)

        ttk.Button(self, text="Generate Summary", command=self.generate_summary).grid(row=17, column=0, columnspan=2, pady=10)

        self.summary_text = tk.Text(self, height=8, width=80)
        self.summary_text.grid(row=18, column=0, columnspan=2, pady=10)

    def generate_summary(self):
        name = self.system_name.get().strip()
        desc = self.system_desc.get("1.0", tk.END).strip()
        scenarios = [e.get().strip() for e in self.scenarios if e.get().strip()]
        classes = [e.get().strip() for e in self.key_classes if e.get().strip()]
        subs = [e.get().strip() for e in self.subsystems if e.get().strip()]

        summary = f"System: {name}\nDescription: {desc}\n\n"
        summary += f"NSS (Number of Scenario Scripts): {len(scenarios)}\n"
        for i, s in enumerate(scenarios, 1):
            summary += f"  {i}. {s}\n"
        summary += f"\nNKC (Number of Key Classes): {len(classes)}\n"
        for c in classes:
            summary += f"  - {c}\n"
        summary += f"\nNSU (Number of Subsystems): {len(subs)}\n"
        for s in subs:
            summary += f"  - {s}\n"

        if len(subs) >= 3 and len(scenarios) >= 3:
            scale = "System is large-scale (high complexity)."
        elif len(subs) >= 2 and len(scenarios) >= 2:
            scale = "System is medium-scale."
        else:
            scale = "System is small-scale."
        summary += f"\nScale Assessment: {scale}"

        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary)

class ApplicationCompositionFrame(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Application Composition Model (Step 1)", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
        ttk.Label(self, text="Select System:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.system_var = tk.StringVar()
        self.system_combo = ttk.Combobox(self, textvariable=self.system_var, values=variant_data.get_system_names(), width=20)
        self.system_combo.grid(row=1, column=1, padx=5)
        self.system_combo.bind("<<ComboboxSelected>>", self.on_system_selected)

        self.labels = {}
        row = 2
        fields = [
            ("Screens (S/M/H):", "screens"),
            ("Reports (S/M/H):", "reports"),
            ("3GL modules:", "gl3"),
            ("Productivity (PROD):", "prod")
        ]
        for label, key in fields:
            ttk.Label(self, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            self.labels[key] = ttk.Label(self, text="", relief=tk.SUNKEN, width=25)
            self.labels[key].grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            row += 1

        ttk.Button(self, text="Calculate Object Points", command=self.calculate).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        self.result_text = tk.Text(self, height=12, width=70)
        self.result_text.grid(row=row, column=0, columnspan=3, pady=10)

    def on_system_selected(self, event):
        system = self.system_var.get()
        comp = variant_data.get_composition(system)
        screens = f"{comp[0]} S / {comp[1]} M / {comp[2]} H"
        reports = f"{comp[3]} S / {comp[4]} M / {comp[5]} H"
        self.labels["screens"].config(text=screens)
        self.labels["reports"].config(text=reports)
        self.labels["gl3"].config(text=str(comp[6]))
        self.labels["prod"].config(text=comp[7])

    def calculate(self):
        system = self.system_var.get()
        if not system:
            messagebox.showwarning("Warning", "Please select a system first.")
            return
        comp = variant_data.get_composition(system)

        screen_weights = {"S": 1, "M": 2, "H": 3}
        report_weights = {"S": 2, "M": 5, "H": 8}
        gl3_weight = 10

        screens_s, screens_m, screens_h = comp[0], comp[1], comp[2]
        reports_s, reports_m, reports_h = comp[3], comp[4], comp[5]
        gl3 = comp[6]
        prod_label = comp[7]

        op = (screens_s * screen_weights["S"] +
              screens_m * screen_weights["M"] +
              screens_h * screen_weights["H"] +
              reports_s * report_weights["S"] +
              reports_m * report_weights["M"] +
              reports_h * report_weights["H"] +
              gl3 * gl3_weight)

        prod_map = {
            "Very Low": 5,
            "Low": 7,
            "High": 10,
            "Very High": 12,
            "Extra High": 15
        }
        prod = prod_map.get(prod_label, 10)
        reuse = 0.20
        effort_pm = (op * (1 - reuse)) / prod
        months_target = 3
        devs_needed = effort_pm / months_target
        low_prod = 5
        effort_low_prod = (op * (1 - reuse)) / low_prod
        impact_days = (effort_low_prod - effort_pm) * 20
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"** Object Points Calculation **\n")
        self.result_text.insert(tk.END, f"Total Object Points (OP): {op:.2f}\n")
        self.result_text.insert(tk.END, f"Productivity (PROD): {prod} OP/person-month\n")
        self.result_text.insert(tk.END, f"Effort (person-months): {effort_pm:.2f} PM\n\n")
        self.result_text.insert(tk.END, f"** Managerial Report **\n")
        self.result_text.insert(tk.END, f"To finish in 3 months, you need ~{devs_needed:.1f} developers.\n")
        self.result_text.insert(tk.END, f"If productivity is Very Low (5 OP/PM), effort becomes {effort_low_prod:.2f} PM, "
                                        f"which is {impact_days:.0f} extra working days.\n")
        self.result_text.insert(tk.END, "Low productivity directly extends the schedule. "
                                        "Consider training or hiring more experienced developers.\n")

class CouplingAnalysisFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Coupling Analysis (Step 4)", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Select System:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.system_var = tk.StringVar()
        systems = [
            "SmartClinic", "AeroCheck", "EcoLogistics", "FoodDash", "EduPortal",
            "BankGuard", "FitTrack Pro", "AutoPart Finder", "GreenEnergy Grid", "CinemaBooking",
            "PetHotel", "Warehouse360", "CryptoWallet", "RealEstate Scan", "SmartHome Hub",
            "EventMaster", "SteamCloud Shop", "LawCase Manager", "TaxiRide Core", "LibraryNext"
        ]
        self.system_combo = ttk.Combobox(self, textvariable=self.system_var, values=systems, width=20)
        self.system_combo.grid(row=1, column=1, padx=5)
        self.system_combo.bind("<<ComboboxSelected>>", self.on_system_selected)

        self.coupling_data = {
            "SmartClinic": {
                "classA": "Doctor", "classB": "ERecipe",
                "tight_desc": "Весь об'єкт Patient та History",
                "loose_desc": "patientID та drugCode"
            },
            "AeroCheck": {
                "classA": "GateControl", "classB": "BoardingPass",
                "tight_desc": "Об'єкт Passenger зі всіма візами",
                "loose_desc": "ticketID та gateStatus"
            },
            "EcoLogistics": {
                "classA": "Route", "classB": "GPS_Tracker",
                "tight_desc": "Весь список Waypoints та Cargo",
                "loose_desc": "currentCoords та speed"
            },
            "FoodDash": {
                "classA": "Courier", "classB": "PayoutSystem",
                "tight_desc": "Об'єкт Order з переліком страв",
                "loose_desc": "orderID та deliveryFee"
            },
            "EduPortal": {
                "classA": "Student", "classB": "Certificate",
                "tight_desc": "Весь GradeBook за всі роки",
                "loose_desc": "courseID та finalScore"
            },
            "BankGuard": {
                "classA": "Transaction", "classB": "FraudEngine",
                "tight_desc": "Об'єкт Cardholder з адресою",
                "loose_desc": "amount та merchantCategory"
            },
            "FitTrack Pro": {
                "classA": "Workout", "classB": "CalorieCalc",
                "tight_desc": "Об'єкт User з антропометрією",
                "loose_desc": "activityType та duration"
            },
            "AutoPart Finder": {
                "classA": "Store", "classB": "Shipping",
                "tight_desc": "Об'єкт Customer з кошиком",
                "loose_desc": "weight та zipCode"
            },
            "GreenEnergy Grid": {
                "classA": "Sensor", "classB": "MainInverter",
                "tight_desc": "Весь лог VoltageHistory",
                "loose_desc": "currentVoltage"
            },
            "CinemaBooking": {
                "classA": "Ticket", "classB": "Printer",
                "tight_desc": "Об'єкт Movie з описом та акторами",
                "loose_desc": "seat та bookingTime"
            },
            "PetHotel": {
                "classA": "Booking", "classB": "VaccineCheck",
                "tight_desc": "Весь об'єкт Pet з родоводом",
                "loose_desc": "petType та vaxDate"
            },
            "Warehouse360": {
                "classA": "Robot", "classB": "Inventory",
                "tight_desc": "Весь об'єкт Shelf з координатами",
                "loose_desc": "skuCode та actionType"
            },
            "CryptoWallet": {
                "classA": "Trade", "classB": "TaxCalculator",
                "tight_desc": "Весь WalletHistory",
                "loose_desc": "profitAmount та assetType"
            },
            "RealEstate Scan": {
                "classA": "Agent", "classB": "AdPublisher",
                "tight_desc": "Об'єкт Property з кресленнями",
                "loose_desc": "price та squareMeters"
            },
            "SmartHome Hub": {
                "classA": "Light", "classB": "ElectricityMeter",
                "tight_desc": "Об'єкт Room зі списком меблів",
                "loose_desc": "devicePower та state"
            },
            "EventMaster": {
                "classA": "Guest", "classB": "BadgeGenerator",
                "tight_desc": "Весь профіль LinkedIn",
                "loose_desc": "fullName та roleType"
            },
            "SteamCloud Shop": {
                "classA": "Achievement", "classB": "UserRank",
                "tight_desc": "Весь об'єкт GameStats",
                "loose_desc": "xpPoints та isTrophy"
            },
            "LawCase Manager": {
                "classA": "Judge", "classB": "CourtVerdict",
                "tight_desc": "Весь об'єкт Evidence (докази)",
                "loose_desc": "caseID та verdictStatus"
            },
            "TaxiRide Core": {
                "classA": "Driver", "classB": "RatingSystem",
                "tight_desc": "Об'єкт Trip з маршрутом на карті",
                "loose_desc": "rating та tripDuration"
            },
            "LibraryNext": {
                "classA": "Reader", "classB": "FineCalculator",
                "tight_desc": "Весь список BorrowedBooks",
                "loose_desc": "overdueDays та bookTier"
            }
        }

        ttk.Label(self, text="Class A (Sender):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.classA_label = ttk.Label(self, text="", relief=tk.SUNKEN, width=30)
        self.classA_label.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(self, text="Class B (Receiver):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.classB_label = ttk.Label(self, text="", relief=tk.SUNKEN, width=30)
        self.classB_label.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(self, text="Tight Coupling Scenario (passes full object):", font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.tight_text = tk.Text(self, height=3, width=70)
        self.tight_text.grid(row=5, column=0, columnspan=2, padx=5, pady=2)

        ttk.Label(self, text="Loose Coupling Scenario (passes minimal data):", font=("Arial", 10, "bold")).grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.loose_text = tk.Text(self, height=3, width=70)
        self.loose_text.grid(row=7, column=0, columnspan=2, padx=5, pady=2)

        ttk.Button(self, text="Analyze Coupling", command=self.analyze).grid(row=8, column=0, columnspan=2, pady=10)

        self.analysis_text = tk.Text(self, height=12, width=80)
        self.analysis_text.grid(row=9, column=0, columnspan=2, pady=10)

    def on_system_selected(self, event):
        system = self.system_var.get()
        data = self.coupling_data.get(system, {})
        self.classA_label.config(text=data.get("classA", ""))
        self.classB_label.config(text=data.get("classB", ""))
        self.tight_text.delete(1.0, tk.END)
        self.tight_text.insert(tk.END, data.get("tight_desc", ""))
        self.loose_text.delete(1.0, tk.END)
        self.loose_text.insert(tk.END, data.get("loose_desc", ""))

    def analyze(self):
        system = self.system_var.get()
        data = self.coupling_data.get(system)
        if not data:
            messagebox.showwarning("Warning", "Please select a system first.")
            return
        classA = data["classA"]
        classB = data["classB"]
        tight = data["tight_desc"]
        loose = data["loose_desc"]

        analysis = f"**Analysis for {system}**\n\n"
        analysis += f"Class A: {classA}\nClass B: {classB}\n\n"
        analysis += "**Tight Coupling (Scenario A):**\n"
        analysis += f"  - Передається: {tight}\n"
        analysis += "  - Недоліки: Клас A залежить від внутрішньої структури класу B. "
        analysis += "Будь-яка зміна в B (наприклад, перейменування поля) змусить змінювати A. "
        analysis += "Fan-out класу A збільшується, оскільки він знає про багато деталей B.\n\n"

        analysis += "**Loose Coupling (Scenario B):**\n"
        analysis += f"  - Передається: {loose}\n"
        analysis += "  - Переваги: Клас A передає лише мінімальну інформацію (ID, ключові параметри). "
        analysis += "Fan-out зменшується, оскільки A не залежить від структури B. "
        analysis += "Заміна технології в класі B (наприклад, зміна сервісу друку або платіжної системи) "
        analysis += "не вплине на A — достатньо оновити лише B.\n\n"

        analysis += "**Бізнес-кейс 'Заміна модуля':**\n"
        analysis += "У сценарії B (слабка зв'язність) заміна платіжної системи або друку займе близько 1 години, "
        analysis += "оскільки клас A не залежить від конкретної реалізації. У сценарії A зміни можуть "
        analysis += "призвести до переписування всієї системи через численні залежності.\n\n"

        analysis += "**Висновок:** Рекомендується використовувати слабку зв'язність (передавати мінімум даних) "
        analysis += "для підвищення гнучкості та зменшення ризиків при змінах."

        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, analysis)

class ManagementReportFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Management Report (Step 5)", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="SI (Specialization Index):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.si_entry = ttk.Entry(self, width=10)
        self.si_entry.grid(row=1, column=1, padx=5)

        ttk.Label(self, text="WMC:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.wmc_entry = ttk.Entry(self, width=10)
        self.wmc_entry.grid(row=2, column=1, padx=5)

        ttk.Label(self, text="CBO:").grid(row=3, column=0, sticky=tk.W, padx=5)
        self.cbo_entry = ttk.Entry(self, width=10)
        self.cbo_entry.grid(row=3, column=1, padx=5)

        ttk.Label(self, text="LCOM:").grid(row=4, column=0, sticky=tk.W, padx=5)
        self.lcom_entry = ttk.Entry(self, width=10)
        self.lcom_entry.grid(row=4, column=1, padx=5)

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=5, column=0, columnspan=2, pady=10)

        self.report_text = tk.Text(self, height=20, width=80)
        self.report_text.grid(row=6, column=0, columnspan=2, pady=10)

    def generate_report(self):
        try:
            si = float(self.si_entry.get()) if self.si_entry.get() else 0.0
            wmc = float(self.wmc_entry.get()) if self.wmc_entry.get() else 0.0
            cbo = float(self.cbo_entry.get()) if self.cbo_entry.get() else 0.0
            lcom = float(self.lcom_entry.get()) if self.lcom_entry.get() else 0.0
        except ValueError:
            messagebox.showerror("Error", "Please enter numeric values for metrics.")
            return


        thresholds = {'WMC': 40, 'CBO': 15, 'LCOM': 0.5, 'SI': 0.5}

        report = "MANAGEMENT REPORT\n"
        report += "="*40 + "\n\n"


        if wmc > thresholds['WMC'] or cbo > thresholds['CBO']:
            report += "❌ **Архітектура НЕ готова до впровадження нових модулів.**\n"
            report += "   Високі показники WMC або CBO можуть спричинити 'ефект доміно' при змінах.\n\n"
        else:
            report += "✅ **Архітектура готова до розширення.**\n\n"


        risks = []
        if si > 0.8:
            risks.append(f"SI = {si:.2f} (>0.8): Проблема в ієрархії — нащадки надто сильно змінюють батьківську логіку.")
        if cbo > 15:
            risks.append(f"CBO = {cbo:.0f} (>15): Надмірна зв'язність — система заплутана.")
        if lcom > 0.7:
            risks.append(f"LCOM = {lcom:.2f} (>0.7): Клас виконує забагато несхожих функцій (низька зв'язність).")

        report += "**Діагностика ризиків:**\n"
        if risks:
            for r in risks:
                report += f"  - {r}\n"
        else:
            report += "  - Усі ключові показники в нормі.\n"
        report += "\n"

        # 3) Priority refactoring step
        report += "**Пріоритетний крок рефакторингу:**\n"
        if wmc > 40:
            report += "  - Розділити God Object на дрібні класи.\n"
        elif cbo > 15:
            report += "  - Впровадити інтерфейси для зменшення зв'язності (CBO).\n"
        elif si > 0.5:
            report += "  - Спростити ієрархію успадкування (використати композицію).\n"
        elif lcom > 0.7:
            report += "  - Розбити клас на логічно пов'язані модулі.\n"
        else:
            report += "  - Архітектура в задовільному стані; можна продовжувати розробку без термінових змін.\n"
        report += "\n"

        report += "**Фінальний вердикт:**\n"
        if wmc > 40 or cbo > 20 or lcom > 0.9:
            report += "  Негайно переписати архітектуру. Технічний борг загрожує зривом термінів.\n"
        elif wmc > 20 or cbo > 12 or lcom > 0.6:
            report += "  Провести частковий рефакторинг. Код потребує покращення перед масштабуванням.\n"
        else:
            report += "  Залишити як є. Архітектура відповідає вимогам.\n"

        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Software Metrics & Planning Tool")
        self.geometry("1000x800")

        sidebar = ttk.Frame(self, width=200, relief=tk.SUNKEN)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        buttons = [
            ("Conceptual Design", self.show_conceptual),
            ("Application Composition", self.show_composition),
            ("Hierarchy Analyzer", self.show_hierarchy),
            ("CK Metrics", self.show_ck),
            ("MOOD Analyzer", self.show_mood),
            ("UCP Calculator", self.show_ucp),
            ("PERT Risk Engine", self.show_pert),
            ("Commercial Proposal", self.show_proposal),
            ("Coupling Analysis", self.show_coupling),
            ("Management Report", self.show_report)
        ]
        for text, cmd in buttons:
            ttk.Button(sidebar, text=text, command=cmd).pack(fill=tk.X, padx=5, pady=5)

        self.frames = {}
        self.frames['Conceptual'] = ConceptualDesignFrame(self.main_frame)
        self.frames['Composition'] = ApplicationCompositionFrame(self.main_frame)
        self.frames['Hierarchy'] = HierarchyAnalyzerFrame(self.main_frame)
        self.frames['CK'] = CKMetricsFrame(self.main_frame)
        self.frames['MOOD'] = MOODAnalyzerFrame(self.main_frame)
        self.ucp_frame = UCPCalculatorFrame(self.main_frame)
        self.frames['UCP'] = self.ucp_frame
        self.pert_frame = PERTRiskEngineFrame(self.main_frame)
        self.frames['PERT'] = self.pert_frame
        self.proposal_frame = CommercialProposalFrame(self.main_frame)
        self.proposal_frame.app = self
        self.frames['Proposal'] = self.proposal_frame
        self.frames['Coupling'] = CouplingAnalysisFrame(self.main_frame)
        self.frames['Report'] = ManagementReportFrame(self.main_frame)

        self.show_conceptual()

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill=tk.BOTH, expand=True)

    def show_conceptual(self):
        self.show_frame('Conceptual')
    def show_composition(self):
        self.show_frame('Composition')
    def show_hierarchy(self):
        self.show_frame('Hierarchy')
    def show_ck(self):
        self.show_frame('CK')
    def show_mood(self):
        self.show_frame('MOOD')
    def show_ucp(self):
        self.show_frame('UCP')
    def show_pert(self):
        self.show_frame('PERT')
    def show_proposal(self):
        self.show_frame('Proposal')
    def show_coupling(self):
        self.show_frame('Coupling')
    def show_report(self):
        self.show_frame('Report')

if __name__ == "__main__":
    app = Application()
    app.mainloop()