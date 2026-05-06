import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ================= DATABASE =================
conn = sqlite3.connect("health_management.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTO_INCREMENT,
username TEXT UNIQUE,
password TEXT,
role TEXT)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients(
id INTEGER PRIMARY KEY AUTO_INCREMENT,
username TEXT,
name TEXT,
age INTEGER,
gender TEXT,
height REAL,
weight REAL,
bmi REAL,
disease TEXT,
doctor_assigned TEXT,
date TEXT)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors(
id INTEGER PRIMARY KEY AUTO_INCREMENT,
name TEXT,
specialization TEXT,
contact TEXT,
date TEXT)
""")

cursor.execute("""
INSERT OR IGNORE INTO users VALUES(null,'admin','admin123','Admin')
""")
conn.commit()

# ================= MAIN APP =================
class HealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Management System")
        self.root.geometry("1400x780")
        self.current_username = None
        self.current_user_role = None
        self.login_screen()

    # ---------------- LOGIN ----------------
    def login_screen(self):
        self.clear_screen()
        card = tk.Frame(self.root, bg="white", padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="Hospital Login", font=("Segoe UI", 24, "bold"),
                 bg="white").pack(pady=20)

        ttk.Label(card, text="Username").pack(anchor="w")
        self.username_entry = ttk.Entry(card, width=30)
        self.username_entry.pack()

        ttk.Label(card, text="Password").pack(anchor="w")
        self.password_entry = ttk.Entry(card, show="*", width=30)
        self.password_entry.pack()

        ttk.Button(card, text="Login", command=self.login).pack(pady=10)
        ttk.Button(card, text="Create Account",
                   command=self.create_account_screen).pack()

    def login(self):
        u = self.username_entry.get()
        p = self.password_entry.get()
        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (u, p))
        r = cursor.fetchone()
        if r:
            self.current_username = u
            self.current_user_role = r[0]
            self.dashboard()
        else:
            messagebox.showerror("Error", "Invalid Login")

    # ---------------- CREATE ACCOUNT ----------------
    def create_account_screen(self):
        self.clear_screen()
        card = tk.Frame(self.root, bg="white", padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="Create Account", font=("Segoe UI", 22, "bold")).pack(pady=15)

        u = ttk.Entry(card, width=30)
        p = ttk.Entry(card, show="*", width=30)
        r = ttk.Combobox(card, values=["Patient", "Receptionist", "Doctor"],
                         state="readonly", width=28)

        for label, widget in [("Username", u), ("Password", p), ("Role", r)]:
            ttk.Label(card, text=label).pack(anchor="w")
            widget.pack(pady=5)

        def save():
            try:
                cursor.execute("INSERT INTO users VALUES(null,?,?,?)",
                               (u.get(), p.get(), r.get()))
                conn.commit()
                messagebox.showinfo("Success", "Account Created")
                self.login_screen()
            except:
                messagebox.showerror("Error", "Username already exists")

        ttk.Button(card, text="Create", command=save).pack(pady=10)
        ttk.Button(card, text="Back", command=self.login_screen).pack()

    # ---------------- DASHBOARD ----------------
    def dashboard(self):
        self.clear_screen()

        sidebar = tk.Frame(self.root, bg="#0F172A", width=220)
        sidebar.pack(side="left", fill="y")

        def menu(t, c):
            tk.Button(sidebar, text=t, fg="white", bg="#0F172A",
                      font=("Segoe UI", 12), bd=0,
                      command=c).pack(fill="x", pady=6)

        menu("Home", self.show_home)

        if self.current_user_role in ["Admin", "Receptionist"]:
            menu("Add Patient", self.add_patient)

        if self.current_user_role == "Receptionist":
            menu("Add Doctor", self.add_doctor)
            menu("Doctor Records", self.show_doctors)

        menu("Patient Records", self.show_patients)
        menu("Logout", self.login_screen)

        self.main = tk.Frame(self.root, bg="#F1F5F9")
        self.main.pack(fill="both", expand=True)
        self.show_home()

    def show_home(self):
        self.clear_main()
        tk.Label(self.main, text=f"Welcome {self.current_username}",
                 font=("Segoe UI", 26, "bold"),
                 bg="#F1F5F9").pack(pady=50)

    # ---------------- ADD PATIENT ----------------
    def add_patient(self):
        self.clear_main()
        card = tk.Frame(self.main, bg="white", padx=40, pady=40)
        card.pack(pady=40)

        fields = {}
        labels = ["Name", "Age", "Height (cm)", "Weight (kg)", "Disease"]

        for i, l in enumerate(labels):
            ttk.Label(card, text=l).grid(row=i, column=0, sticky="w")
            e = ttk.Entry(card, width=30)
            e.grid(row=i, column=1)
            fields[l] = e

        ttk.Label(card, text="Gender").grid(row=5, column=0, sticky="w")
        gender = ttk.Combobox(card, values=["Male", "Female", "Other"],
                              state="readonly", width=28)
        gender.grid(row=5, column=1)

        ttk.Label(card, text="Doctor").grid(row=6, column=0, sticky="w")
        cursor.execute("SELECT name FROM doctors")
        doctor = ttk.Combobox(card, values=[d[0] for d in cursor.fetchall()],
                              state="readonly", width=28)
        doctor.grid(row=6, column=1)

        def save():
            h = float(fields["Height (cm)"].get())
            w = float(fields["Weight (kg)"].get())
            bmi = round(w / ((h / 100) ** 2), 2)

            cursor.execute("""
            INSERT INTO patients VALUES(null,?,?,?,?,?,?,?,?,?)
            """, (
                self.current_username,
                fields["Name"].get(),
                int(fields["Age"].get()),
                gender.get(),
                h, w, bmi,
                fields["Disease"].get(),
                doctor.get(),
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))
            conn.commit()
            messagebox.showinfo("Success", "Patient Added")

        ttk.Button(card, text="Save Patient", command=save)\
            .grid(row=7, columnspan=2, pady=20)

    # ---------------- PATIENT RECORDS ----------------
    def show_patients(self):
        self.clear_main()
        frame = tk.Frame(self.main, bg="white")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        cols = ("ID","Name","Age","Gender","Height","Weight",
                "BMI","Disease","Doctor","Date & Time")

        tree = ttk.Treeview(frame, columns=cols, show="headings")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)

        tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150)

        if self.current_user_role == "Patient":
            cursor.execute("""
            SELECT id,name,age,gender,height,weight,bmi,disease,doctor_assigned,date
            FROM patients WHERE username=?
            """, (self.current_username,))
        else:
            cursor.execute("""
            SELECT id,name,age,gender,height,weight,bmi,disease,doctor_assigned,date
            FROM patients
            """)

        for r in cursor.fetchall():
            tree.insert("", "end", values=r)

    # ---------------- DOCTORS ----------------
    def add_doctor(self):
        self.clear_main()
        card = tk.Frame(self.main, bg="white", padx=40, pady=40)
        card.pack(pady=40)

        e = {}
        for i, t in enumerate(["Name", "Specialization", "Contact"]):
            ttk.Label(card, text=t).grid(row=i, column=0)
            e[t] = ttk.Entry(card, width=30)
            e[t].grid(row=i, column=1)

        def save():
            cursor.execute("""
            INSERT INTO doctors VALUES(null,?,?,?,?)
            """, (
                e["Name"].get(), e["Specialization"].get(),
                e["Contact"].get(),
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))
            conn.commit()
            messagebox.showinfo("Success", "Doctor Added")

        ttk.Button(card, text="Save Doctor", command=save)\
            .grid(row=3, columnspan=2, pady=15)

    def show_doctors(self):
        self.clear_main()
        frame = tk.Frame(self.main, bg="white")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        cols = ("ID","Name","Specialization","Contact","Date")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        tree.pack(fill="both", expand=True)

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=200)

        cursor.execute("SELECT * FROM doctors")
        for r in cursor.fetchall():
            tree.insert("", "end", values=r)

    # ---------------- HELPERS ----------------
    def clear_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

# ================= RUN =================
root = tk.Tk()
HealthApp(root)
root.mainloop()
