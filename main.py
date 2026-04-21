import tkinter as tk
from tkinter import ttk, messagebox
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# ---------------- Grover Components ---------------- #

def grover_oracle(qc, target):
    n = len(target)
    for i in range(n):
        if target[i] == '0':
            qc.x(i)
    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)
    for i in range(n):
        if target[i] == '0':
            qc.x(i)

def diffusion(qc, n):
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)
    qc.x(range(n))
    qc.h(range(n))

# ---------------- Algorithm Logic ---------------- #

def run_simulation():
    selected_algo = algorithm_var.get()

    if selected_algo == "Deutsch-Jozsa":
        run_deutsch_jozsa()
    elif selected_algo == "Grover":
        run_grover()
    elif selected_algo == "Bernstein-Vazirani":
        run_bv()
    else:
        messagebox.showinfo("Info", "Algorithm not implemented yet.")

# ---------------- Deutsch-Jozsa ---------------- #

def run_deutsch_jozsa():
    try:
        n = int(qubit_entry.get())
        shots = int(shots_entry.get())
        oracle_choice = oracle_var.get()

        qc = QuantumCircuit(n + 1, n)

        qc.x(n)
        qc.h(range(n + 1))

        if oracle_choice == "Balanced":
            for i in range(n):
                qc.cx(i, n)
        elif oracle_choice == "Constant (1)":
            qc.x(n)

        qc.h(range(n))
        qc.measure(range(n), range(n))

        qc.draw("mpl")
        plt.title("Deutsch-Jozsa Circuit")
        plt.show()

        simulator = Aer.get_backend("qasm_simulator")
        result = simulator.run(qc, shots=shots).result()
        counts = result.get_counts()

        plot_histogram(counts)
        plt.title("Measurement Results")
        plt.show()

        if "0" * n in counts:
            explanation = (
                "Result Analysis: DEUTSCH–JOZSA ALGORITHM\n\n"
                "• Output is all zeros → constructive interference.\n\n"
                "Conclusion:\n"
                "• Function is CONSTANT.\n"
            )
        else:
            explanation = (
                "Result Analysis: DEUTSCH–JOZSA ALGORITHM\n\n"
                "• Non-zero outputs observed → destructive interference.\n\n"
                "Conclusion:\n"
                "• Function is BALANCED.\n"
            )

        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, explanation)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- Grover ---------------- #

def run_grover():
    try:
        n = int(qubit_entry.get())
        shots = int(shots_entry.get())
        target = target_entry.get().strip()

        if len(target) != n:
            messagebox.showerror("Error", f"Target must be {n} bits long")
            return

        qc = QuantumCircuit(n, n)
        qc.h(range(n))

        import math
        iterations = max(1, int((math.pi/4) * (2**(n/2))))

        for _ in range(iterations):
            grover_oracle(qc, target[::-1])
            diffusion(qc, n)

        qc.measure(range(n), range(n))

        qc.draw("mpl")
        plt.title("Grover Circuit")
        plt.show()

        simulator = Aer.get_backend("qasm_simulator")
        result = simulator.run(qc, shots=shots).result()
        counts = result.get_counts()

        plot_histogram(counts)
        plt.title("Grover Results")
        plt.show()

        explanation = (
            f"Result Analysis: GROVER'S ALGORITHM\n\n"
            f"Target State: {target}\n\n"
            "• Oracle marks target\n"
            "• Diffusion amplifies probability\n\n"
            "Conclusion:\n"
            "• Target state appears with highest probability.\n"
        )

        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, explanation)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- Bernstein-Vazirani ---------------- #

def run_bv():
    try:
        n = int(qubit_entry.get())
        shots = int(shots_entry.get())
        secret = target_entry.get().strip()

        if len(secret) != n:
            messagebox.showerror("Error", f"Secret string must be {n} bits long")
            return

        qc = QuantumCircuit(n + 1, n)

        qc.x(n)
        qc.h(range(n + 1))

        for i in range(n):
            if secret[i] == '1':
                qc.cx(i, n)

        qc.h(range(n))
        qc.measure(range(n), range(n))

        qc.draw("mpl")
        plt.title("Bernstein-Vazirani Circuit")
        plt.show()

        simulator = Aer.get_backend("qasm_simulator")
        result = simulator.run(qc, shots=shots).result()
        counts = result.get_counts()

        plot_histogram(counts)
        plt.title("BV Results")
        plt.show()

        explanation = (
            f"Result Analysis: BERNSTEIN–VAZIRANI\n\n"
            f"Hidden String: {secret}\n\n"
            "• Oracle encodes hidden string\n"
            "• Extracted in one query\n\n"
            "Conclusion:\n"
            "• Hidden string successfully determined.\n"
        )

        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, explanation)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- Dynamic UI ---------------- #

def update_parameters(event=None):
    selected_algo = algorithm_var.get()

    oracle_frame.pack_forget()
    target_frame.pack_forget()

    if selected_algo == "Deutsch-Jozsa":
        oracle_frame.pack(pady=5)
    elif selected_algo in ["Grover", "Bernstein-Vazirani"]:
        target_frame.pack(pady=5)

# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("Quantum Algorithm Simulation Tool")
root.geometry("500x650")

tk.Label(root, text="Quantum Algorithm Simulation Tool",
         font=("Arial", 16, "bold")).pack(pady=10)

tk.Label(root, text="Select Algorithm:").pack()

algorithm_var = tk.StringVar()
algorithm_dropdown = ttk.Combobox(root, textvariable=algorithm_var)
algorithm_dropdown["values"] = ("Deutsch-Jozsa", "Grover", "Bernstein-Vazirani")
algorithm_dropdown.current(0)
algorithm_dropdown.pack(pady=5)

algorithm_dropdown.bind("<<ComboboxSelected>>", update_parameters)

tk.Label(root, text="Parameters", font=("Arial", 12, "bold")).pack(pady=10)

tk.Label(root, text="Number of Input Qubits:").pack()
qubit_entry = tk.Entry(root)
qubit_entry.insert(0, "2")
qubit_entry.pack(pady=5)

tk.Label(root, text="Number of Shots:").pack()
shots_entry = tk.Entry(root)
shots_entry.insert(0, "1024")
shots_entry.pack(pady=5)

# Oracle Frame
oracle_frame = tk.Frame(root)
tk.Label(oracle_frame, text="Oracle Type:").pack()

oracle_var = tk.StringVar()
oracle_dropdown = ttk.Combobox(oracle_frame, textvariable=oracle_var)
oracle_dropdown["values"] = ("Balanced", "Constant (0)", "Constant (1)")
oracle_dropdown.current(0)
oracle_dropdown.pack(pady=5)

# Target Frame
target_frame = tk.Frame(root)
tk.Label(target_frame, text="Target / Secret String:").pack()
target_entry = tk.Entry(target_frame)
target_entry.insert(0, "11")
target_entry.pack(pady=5)

oracle_frame.pack(pady=5)

tk.Button(root, text="Run Simulation",
          command=run_simulation,
          bg="#2196F3", fg="white").pack(pady=20)

tk.Label(root, text="Result Explanation",
         font=("Arial", 12, "bold")).pack()

result_text = tk.Text(root, height=10, width=70, wrap="word",
                      font=("Arial", 10), bg="#f5f5f5")
result_text.pack(pady=10)

root.mainloop()