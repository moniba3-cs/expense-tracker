import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import date
import os

FILE = "expenses.csv"

def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    return pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])

def save_data(df):
    df.to_csv(FILE, index=False)

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Expense Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e2e")

        self.df = load_data()
        self.build_ui()

    def build_ui(self):
    
        tk.Label(self.root, text="💰 Expense Tracker", font=("Helvetica", 20, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=10)

        input_frame = tk.Frame(self.root, bg="#313244", padx=10, pady=10)
        input_frame.pack(fill="x", padx=20)

    
        tk.Label(input_frame, text="Category", bg="#313244", fg="white").grid(row=0, column=0, padx=5)
        self.category = ttk.Combobox(input_frame, values=["Food", "Transport", "Shopping", "Bills", "Health", "Other"], width=12)
        self.category.grid(row=1, column=0, padx=5)
        self.category.set("Food")


        tk.Label(input_frame, text="Description", bg="#313244", fg="white").grid(row=0, column=1, padx=5)
        self.desc = tk.Entry(input_frame, width=20)
        self.desc.grid(row=1, column=1, padx=5)


        tk.Label(input_frame, text="Amount ($)", bg="#313244", fg="white").grid(row=0, column=2, padx=5)
        self.amount = tk.Entry(input_frame, width=10)
        self.amount.grid(row=1, column=2, padx=5)

    
        tk.Button(input_frame, text="➕ Add Expense", bg="#a6e3a1", fg="black",
                  font=("Helvetica", 10, "bold"), command=self.add_expense).grid(row=1, column=3, padx=10)

        
        table_frame = tk.Frame(self.root, bg="#1e1e2e")
        table_frame.pack(fill="both", padx=20, pady=10)

        cols = ("Date", "Category", "Description", "Amount")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="🗑 Delete Selected", bg="#f38ba8", fg="black",
                  command=self.delete_expense).pack(side="left", padx=10)

        tk.Button(btn_frame, text="📊 Show Chart", bg="#89b4fa", fg="black",
                  command=self.show_chart).pack(side="left", padx=10)


        self.total_label = tk.Label(self.root, text="Total: $0.00",
                                    font=("Helvetica", 14, "bold"), bg="#1e1e2e", fg="#f9e2af")
        self.total_label.pack(pady=5)

        self.refresh_table()

    def add_expense(self):
        cat = self.category.get()
        desc = self.desc.get().strip()
        amt = self.amount.get().strip()

        if not desc or not amt:
            messagebox.showwarning("Missing Info", "Please fill in all fields!")
            return
        try:
            amt = float(amt)
        except ValueError:
            messagebox.showerror("Invalid Amount", "Amount must be a number!")
            return

        new_row = {"Date": str(date.today()), "Category": cat, "Description": desc, "Amount": amt}
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(self.df)

        self.desc.delete(0, tk.END)
        self.amount.delete(0, tk.END)
        self.refresh_table()

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Nothing Selected", "Please select a row to delete.")
            return
        index = self.tree.index(selected[0])
        self.df = self.df.drop(index).reset_index(drop=True)
        save_data(self.df)
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, row in self.df.iterrows():
            self.tree.insert("", "end", values=(row["Date"], row["Category"], row["Description"], f"${row['Amount']:.2f}"))
        total = self.df["Amount"].sum() if not self.df.empty else 0
        self.total_label.config(text=f"Total Spent: ${total:.2f}")

    def show_chart(self):
        if self.df.empty:
            messagebox.showinfo("No Data", "Add some expenses first!")
            return
        summary = self.df.groupby("Category")["Amount"].sum()

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(summary, labels=summary.index, autopct="%1.1f%%", startangle=140)
        ax.set_title("Spending by Category")

        chart_win = tk.Toplevel(self.root)
        chart_win.title("📊 Expense Chart")
        canvas = FigureCanvasTkAgg(fig, master=chart_win)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
