import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import Calendar
from time import strftime
import pygame
import os


def generate_time_options():
    return [strftime('%H:%M:%S', (datetime.strptime('00:00:00', '%H:%M:%S') + timedelta(minutes=i)).timetuple())
            for i in range(0, 1440, 15)]


def play_ding_sound():
    try:
        # Use the 'ding.wav' file from the Windows default sounds
        default_sound_path = os.path.join(os.environ['WINDIR'], 'Media', 'ding.wav')

        # Check if the file exists
        if os.path.isfile(default_sound_path):
            pygame.mixer.music.load(default_sound_path)
            pygame.mixer.music.play()
        else:
            print(f"Default sound file not found at: {default_sound_path}")
    except pygame.error as e:
        print(f"Error playing sound: {e}")


def schedule_reminder(reminder_time):
    # You can implement your own reminder system here
    # For example, you can use a separate thread to wait until the reminder time and then play an audio reminder.

    # For demonstration purposes, let's just play the sound immediately
    play_ding_sound()


class ToDoApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ToDo App")
        self.tasks = []

        self.tree = ttk.Treeview(self.master, columns=('Task', 'Due Date', 'Status'))
        self.tree.heading('#0', text='ID')
        self.tree.heading('#1', text='Task')
        self.tree.heading('#2', text='Due Date')
        self.tree.heading('#3', text='Status')
        self.tree.pack(padx=10, pady=10)

        self.task_entry = ttk.Entry(self.master, width=30)
        self.task_entry.pack(pady=5)

        # Use tkcalendar for date input
        self.calendar_var = tk.StringVar()
        self.calendar_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.calendar_button = ttk.Button(self.master, text='Select Date', command=self.select_date)
        self.calendar_button.pack(pady=5)

        # Use ttk.Combobox for time input
        self.time_var = tk.StringVar()
        self.time_var.set(datetime.now().strftime('%H:%M:%S'))
        self.time_combobox = ttk.Combobox(self.master, textvariable=self.time_var, values=generate_time_options())
        self.time_combobox.pack(pady=5)

        add_button = ttk.Button(self.master, text='Add Task', command=self.add_task)
        add_button.pack(pady=5)

        remove_button = ttk.Button(self.master, text='Remove Task', command=self.remove_task)
        remove_button.pack(pady=5)

        complete_button = ttk.Button(self.master, text='Mark as Complete', command=self.mark_as_complete)
        complete_button.pack(pady=5)

        self.reminder_var = tk.StringVar()
        self.reminder_var.set('No reminder')

        reminder_label = ttk.Label(self.master, textvariable=self.reminder_var)
        reminder_label.pack(pady=5)

        set_reminder_button = ttk.Button(self.master, text='Set Reminder', command=self.set_reminder)
        set_reminder_button.pack(pady=5)

        # Clock
        self.clock_label = ttk.Label(self.master, text="")
        self.clock_label.pack(pady=5)
        self.update_clock()

        # Initialize pygame mixer for sound
        pygame.mixer.init()

    def update_clock(self):
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        self.clock_label.config(text=current_time)
        self.master.after(1000, self.update_clock)

    def select_date(self):
        top = tk.Toplevel(self.master)
        cal = Calendar(top, font="Arial 14", selectmode='day', cursor="hand1")
        cal.pack(fill="both", expand=True)
        ttk.Button(top, text="OK", command=lambda: self.set_selected_date(cal.selection_get())).pack()

    def set_selected_date(self, selected_date):
        self.calendar_var.set(selected_date)
        self.master.focus_set()

    def add_task(self):
        task_text = self.task_entry.get()
        due_date_text = f"{self.calendar_var.get()} {self.time_var.get()}"

        try:
            due_date = datetime.strptime(due_date_text, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            messagebox.showerror('Error', 'Invalid date format. Use YYYY-MM-DD HH:MM:SS')
            return

        task_id = len(self.tasks) + 1
        self.tasks.append({'id': task_id, 'task': task_text, 'due_date': due_date, 'status': 'Incomplete'})
        self.update_treeview()

    def remove_task(self):
        selected_item = self.tree.selection()

        if selected_item:
            task_id = int(self.tree.item(selected_item, 'text'))
            self.tasks = [task for task in self.tasks if task['id'] != task_id]
            self.update_treeview()

    def mark_as_complete(self):
        selected_item = self.tree.selection()

        if selected_item:
            task_id = int(self.tree.item(selected_item, 'text'))
            for task in self.tasks:
                if task['id'] == task_id:
                    task['status'] = 'Complete'
            self.update_treeview()

    def set_reminder(self):
        selected_item = self.tree.selection()

        if selected_item:
            task_id = int(self.tree.item(selected_item, 'text'))
            for task in self.tasks:
                if task['id'] == task_id:
                    due_date = task['due_date']
                    reminder_time = due_date - timedelta(minutes=15)  # Reminder 15 minutes before due date
                    schedule_reminder(reminder_time)
                    self.reminder_var.set(f'Reminder set for {reminder_time}')

    def update_treeview(self):
        # Clear existing items in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert updated tasks into the treeview
        for task in self.tasks:
            self.tree.insert('', 'end', text=task['id'], values=(task['task'], task['due_date'], task['status']))


if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
