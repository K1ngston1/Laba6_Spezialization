import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# ------------------------------
# Helper functions for calculations
# ------------------------------

def calculate_specialization_index(nm_base, noo, noa):
    """Calculate Specialization Index and return status."""
    if nm_base == 0:
        return 0, "Invalid (NM_base cannot be zero)"
    si = (noo + noa) / nm_base
    status = "Aggressive Inheritance" if si > 0.5 else "Stable"
    return si, status

def calculate_ck_metrics(wmc, dit, cbo, lcom, rfc, thresholds):
    """Check metrics against thresholds and return list of booleans for red flag."""
    return [wmc > thresholds['WMC'], dit > thresholds['DIT'],
            cbo > thresholds['CBO'], lcom > thresholds['LCOM'],
            rfc > thresholds['RFC']]

def calculate_mood(total_methods, hidden_methods, total_attrs, hidden_attrs, coupling_factor, poly_factor):
    """Calculate MOOD metrics percentages."""
    mhf = (hidden_methods / total_methods * 100) if total_methods > 0 else 0
    ahf = (hidden_attrs / total_attrs * 100) if total_attrs > 0 else 0
    cof = coupling_factor * 100  # Assume coupling_factor is already a decimal
    pof = poly_factor * 100
    return ahf, mhf, cof, pof

def calculate_ucp(actors_simple, actors_avg, actors_complex,
                  uc_simple, uc_avg, uc_complex,
                  tcf, ecf, hours_per_ucp=20):
    """Calculate UCP and person-hours."""
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
    """Calculate PERT expected time, standard deviation, and safe deadline."""
    expected = (optimistic + 4 * most_likely + pessimistic) / 6
    sd = (pessimistic - optimistic) / 6
    safe_deadline = expected + 2 * sd
    return expected, sd, safe_deadline

# ------------------------------
# GUI Frames
# ------------------------------

class HierarchyAnalyzerFrame(ttk.Frame):
    """Frame for Hierarchy Analyzer."""
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
        self.l.insert(0, "0")  # Not used in SI but kept for completeness

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
    """Frame for CK Metrics Dashboard."""
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.thresholds = {'WMC': 40, 'DIT': 5, 'CBO': 15, 'LCOM': 50, 'RFC': 50}

    def create_widgets(self):
        ttk.Label(self, text="CK Metrics Dashboard", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Input fields for metrics
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

            # Clear previous results
            for widget in self.results_frame.winfo_children():
                widget.destroy()

            # Display each metric with color
            for i, (metric, val) in enumerate(values.items()):
                color = "red" if flags[i] else "black"
                label = ttk.Label(self.results_frame, text=f"{metric}: {val}", foreground=color)
                label.grid(row=i, column=0, sticky=tk.W, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Please enter numeric values for all metrics.")

class MOODAnalyzerFrame(ttk.Frame):
    """Frame for MOOD Analyzer."""
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
    """Frame for UCP Calculator."""
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="UCP Calculator", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=4, pady=10)

        # Actors
        ttk.Label(self, text="Actors (Simple):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.actors_simple = ttk.Entry(self, width=10)
        self.actors_simple.grid(row=1, column=1, padx=5)
        ttk.Label(self, text="Avg:").grid(row=1, column=2, sticky=tk.W)
        self.actors_avg = ttk.Entry(self, width=10)
        self.actors_avg.grid(row=1, column=3, padx=5)
        ttk.Label(self, text="Complex:").grid(row=1, column=4, sticky=tk.W)
        self.actors_complex = ttk.Entry(self, width=10)
        self.actors_complex.grid(row=1, column=5, padx=5)

        # Use Cases
        ttk.Label(self, text="Use Cases (Simple):").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.uc_simple = ttk.Entry(self, width=10)
        self.uc_simple.grid(row=2, column=1, padx=5)
        ttk.Label(self, text="Avg:").grid(row=2, column=2, sticky=tk.W)
        self.uc_avg = ttk.Entry(self, width=10)
        self.uc_avg.grid(row=2, column=3, padx=5)
        ttk.Label(self, text="Complex:").grid(row=2, column=4, sticky=tk.W)
        self.uc_complex = ttk.Entry(self, width=10)
        self.uc_complex.grid(row=2, column=5, padx=5)

        # Factors
        ttk.Label(self, text="TCF (Technical Complexity Factor):").grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5)
        self.tcf = ttk.Entry(self, width=10)
        self.tcf.grid(row=3, column=2, padx=5, sticky=tk.W)
        ttk.Label(self, text="ECF (Environmental Complexity Factor):").grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5)
        self.ecf = ttk.Entry(self, width=10)
        self.ecf.grid(row=4, column=2, padx=5, sticky=tk.W)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=5, column=0, columnspan=6, pady=10)

        self.result_label = ttk.Label(self, text="", font=("Arial", 10))
        self.result_label.grid(row=6, column=0, columnspan=6)

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
    """Frame for PERT Risk Engine with graph."""
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.fig, self.ax = plt.subplots(figsize=(4, 2))
        self.canvas = None

    def create_widgets(self):
        ttk.Label(self, text="PERT Risk Engine", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Optimistic (O):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.optimistic = ttk.Entry(self, width=10)
        self.optimistic.grid(row=1, column=1, padx=5)

        ttk.Label(self, text="Most Likely (M):").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.most_likely = ttk.Entry(self, width=10)
        self.most_likely.grid(row=2, column=1, padx=5)

        ttk.Label(self, text="Pessimistic (P):").grid(row=3, column=0, sticky=tk.W, padx=5)
        self.pessimistic = ttk.Entry(self, width=10)
        self.pessimistic.grid(row=3, column=1, padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=4, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(self, text="", font=("Arial", 10))
        self.result_label.grid(row=5, column=0, columnspan=2)

        self.graph_frame = ttk.Frame(self)
        self.graph_frame.grid(row=6, column=0, columnspan=2, pady=10)

    def calculate(self):
        try:
            o = float(self.optimistic.get())
            m = float(self.most_likely.get())
            p = float(self.pessimistic.get())

            exp, sd, safe = calculate_pert(o, m, p)

            self.result_label.config(text=f"Expected Time (E): {exp:.2f}\nStd Dev: {sd:.2f}\nSafe Deadline (E+2SD): {safe:.2f}")

            # Clear previous graph
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            self.ax.clear()
            # Create a simple bar chart with color coding
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
    """Frame for Commercial Proposal Generator."""
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

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

        self.result_text = tk.Text(self, height=10, width=50)
        self.result_text.grid(row=4, column=0, columnspan=2, pady=10)

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

# ------------------------------
# Main Application with Sidebar
# ------------------------------

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Software Metrics & Planning Tool")
        self.geometry("900x700")

        # Create sidebar frame
        sidebar = ttk.Frame(self, width=200, relief=tk.SUNKEN)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Main content frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create buttons for navigation
        ttk.Button(sidebar, text="Hierarchy Analyzer", command=self.show_hierarchy).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sidebar, text="CK Metrics", command=self.show_ck).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sidebar, text="MOOD Analyzer", command=self.show_mood).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sidebar, text="UCP Calculator", command=self.show_ucp).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sidebar, text="PERT Risk Engine", command=self.show_pert).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sidebar, text="Commercial Proposal", command=self.show_proposal).pack(fill=tk.X, padx=5, pady=5)

        # Initialize frames
        self.frames = {}
        self.frames['Hierarchy'] = HierarchyAnalyzerFrame(self.main_frame)
        self.frames['CK'] = CKMetricsFrame(self.main_frame)
        self.frames['MOOD'] = MOODAnalyzerFrame(self.main_frame)
        self.frames['UCP'] = UCPCalculatorFrame(self.main_frame)
        self.frames['PERT'] = PERTRiskEngineFrame(self.main_frame)
        self.frames['Proposal'] = CommercialProposalFrame(self.main_frame)

        # Show default frame
        self.show_hierarchy()

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill=tk.BOTH, expand=True)

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

if __name__ == "__main__":
    app = Application()
    app.mainloop()
