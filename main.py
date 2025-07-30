import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import json
import os

EVENT_FILE = "events.json"
DELETED_FILE = "deleted_events.json"

def log_deleted_event(event):
    if not os.path.exists(DELETED_FILE):
        with open(DELETED_FILE, "w") as f:
            json.dump([], f)
    with open(DELETED_FILE, "r") as f:
        old_data = json.load(f)
    old_data.append(event)
    with open(DELETED_FILE, "w") as f:
        json.dump(old_data, f, indent=2)
WHATSNEW_FILE = "whatsnew.json"

def load_events():
    if not os.path.exists(EVENT_FILE):
        with open(EVENT_FILE, "w") as f:
            json.dump([], f)
    with open(EVENT_FILE, "r") as f:
        return json.load(f)

def save_events(events):
    with open(EVENT_FILE, "w") as f:
        json.dump(events, f, indent=2)

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar App")
        self.current_date = datetime.today().replace(day=1)
        self.events = load_events()

        self.header = tk.Label(root, text="", font=("Arial", 16))
        self.header.pack(pady=5)

        self.calendar_frame = tk.Frame(root)
        self.calendar_frame.pack()

        self.draw_calendar()

        # Bottom control bar
        control_frame = tk.Frame(root)
        control_frame.pack(fill="x", pady=10)

        tk.Button(control_frame, text="Prev", width=10, command=self.prev_month).pack(side=tk.LEFT, padx=20)
        tk.Button(control_frame, text="Add Event", width=15, command=self.add_event).pack(side=tk.TOP)
        tk.Button(control_frame, text="What's New", width=15, command=self.show_whats_new).pack(side=tk.TOP, pady=5)
        tk.Button(control_frame, text="Delete", width=15, command=self.delete_event_mode).pack(side=tk.TOP, pady=5)
        tk.Button(control_frame, text="Next", width=10, command=self.next_month).pack(side=tk.RIGHT, padx=20)

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        year = self.current_date.year
        month = self.current_date.month
        self.header.config(text=self.current_date.strftime("%B %Y"))

        first_day = self.current_date
        start_day = first_day.weekday()
        next_month = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1)
        days_in_month = (next_month - timedelta(days=1)).day

        events_by_date = {e["date"]: e for e in self.events}

        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold")).grid(row=0, column=i)

        row = 1
        col = start_day
        for day in range(1, days_in_month + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            text = str(day)
            if date_str in events_by_date:
                text += "\n" + events_by_date[date_str]["title"]

            btn = tk.Button(self.calendar_frame, text=text, width=15, height=4,
                            command=lambda d=date_str: self.show_event(d))
            btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def prev_month(self):
        self.current_date = (self.current_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        self.draw_calendar()

    def next_month(self):
        self.current_date = (self.current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        self.draw_calendar()

    def show_event(self, date_str):
        event = next((e for e in self.events if e["date"] == date_str), None)
        if not event:
            return

        detail = tk.Toplevel(self.root)
        detail.title("Event Details")
        detail.grab_set()

        tk.Label(detail, text="Title: " + event["title"]).pack(padx=10, pady=5)
        tk.Label(detail, text="Date: " + event["date"]).pack(padx=10, pady=5)
        tk.Label(detail, text="Time: " + event.get("time", "")).pack(padx=10, pady=5)
        tk.Label(detail, text="Location: " + event.get("location", "")).pack(padx=10, pady=5)
        tk.Label(detail, text="Notes: " + event.get("notes", "")).pack(padx=10, pady=5)

        tk.Button(detail, text="Edit", command=lambda: [detail.destroy(), self.edit_event_dialog(event)]).pack(pady=10)

    def add_event(self):
        self.edit_event_dialog()

    def edit_event_dialog(self, event=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add/Edit Event")
        dialog.grab_set()

        def make_entry(row, label, initial=""):
            tk.Label(dialog, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(dialog, width=30)
            entry.insert(0, initial)
            entry.grid(row=row, column=1, padx=10, pady=5)
            return entry

        title_entry = make_entry(0, "Title:", event["title"] if event else "")
        date_entry = make_entry(1, "Date (YYYY-MM-DD):", event["date"] if event else "")
        time_entry = make_entry(2, "Time:", event.get("time", "") if event else "")
        location_entry = make_entry(3, "Location:", event.get("location", "") if event else "")
        tk.Label(dialog, text="Notes:").grid(row=4, column=0, padx=10, pady=5, sticky="ne")
        notes_text = tk.Text(dialog, height=5, width=30)
        notes_text.grid(row=4, column=1, padx=10, pady=5)
        if event:
            notes_text.insert("1.0", event.get("notes", ""))

        def confirm():
            new_event = {
                "title": title_entry.get(),
                "date": date_entry.get(),
                "time": time_entry.get(),
                "location": location_entry.get(),
                "notes": notes_text.get("1.0", tk.END).strip()
            }
            if event in self.events:
                log_deleted_event(event)
                self.events.remove(event)
            self.events.append(new_event)
            save_events(self.events)
            self.draw_calendar()
            dialog.destroy()

        def cancel():
            dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(button_frame, text="Confirm", command=confirm).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=10)

    def show_whats_new(self):
        try:
            with open(WHATSNEW_FILE, "r") as f:
                features = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load what's new: {e}")
            return

        popup = tk.Toplevel(self.root)
        popup.title("What's New")
        popup.grab_set()

        for feature, desc in features.items():
            tk.Label(popup, text=f"• {feature}", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)
            tk.Label(popup, text=desc, wraplength=300).pack(anchor="w", padx=20, pady=2)

        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)


    def delete_event_mode(self):
        delete_popup = tk.Toplevel(self.root)
        delete_popup.title("Delete Events")
        delete_popup.grab_set()

        listbox = tk.Listbox(delete_popup, selectmode=tk.MULTIPLE, width=50)
        listbox.pack(padx=10, pady=10)

        for event in self.events:
            display = f"{event['date']} - {event['title']}"
            listbox.insert(tk.END, display)

        def confirm_selection():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showinfo("No selection", "Please select at least one event to delete.")
                return

            # Confirm again
            if not messagebox.askyesno("Confirm Delete", "Are you sure you want to permanently delete the selected event(s)?"):
                return

            selected_events = [self.events[i] for i in selected_indices]
            for ev in selected_events:
                log_deleted_event(ev)
                self.events.remove(ev)

            save_events(self.events)
            self.draw_calendar()
            delete_popup.destroy()

        tk.Button(delete_popup, text="Delete Selected", command=confirm_selection).pack(pady=10)
        tk.Button(delete_popup, text="Cancel", command=delete_popup.destroy).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
