import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import subprocess
import webbrowser
import threading

def update_progress(value):
    def real_update():
        progress_bar['value'] = value
    root.after(0, real_update)

# Function to translate date to numerical format
def translate_date(input_date):
    for char in ".,:;/":
        input_date = input_date.replace(char, "")

    month_dict = {
        #eng
        "January": "01", "january": "01", "Jan": "01", "jan": "01", "Jan.": "01", "jan.": "01",
        "February": "02", "february": "02", "Feb": "02", "feb": "02", "Feb.": "02", "feb.": "02", 
        "March": "03", "march": "03", "Mar": "03", "mar": "03", "Mar.": "03", "mar.": "03", 
        "April": "04", "april": "04", "Apr": "04", "apr": "04","Apr.": "04", "apr.": "04",
        "May": "05", "may": "05", "May.": "05", "may.": "05", 
        "Juni": "06", "juni": "06", "Jun": "06", "jun": "06", "Jun.": "06", "jun.": "06", 
        "July": "07", "july": "07", "Jul": "07", "jul": "07", "Jul.": "07", "jul.": "07", 
        "August": "08", "august": "08", "Aug": "08", "aug": "08", "Aug.": "08", "aug.": "08", 
        "September": "09", "september": "09", "Sep": "09", "sep": "09", "Sep.": "09", "sep.": "09", 
        "October": "10", "october": "10", "Oct": "10", "oct": "10", "Oct.": "10", "oct.": "10", 
        "November": "11", "november": "11", "Nov": "11", "nov": "11", "Nov.": "11", "nov.": "11", 
        "Desember": "12", "desember": "12", "Des": "12", "des": "12", "Des.": "12", "des.": "12",
        #nok
        "Januar": "01", "januar": "01", "Jan": "01", "jan": "01", "Jan.": "01", "jan.": "01",
        "Februar": "02", "februar": "02", "Feb": "02", "feb": "02", "Feb.": "02", "feb.": "02", 
        "Mars": "03", "mars": "03", "Mar": "03", "mar": "03", "Mar.": "03", "mar.": "03", 
        "April": "04", "april": "04", "Apr": "04", "apr": "04","Apr.": "04", "apr.": "04",
        "Mai": "05", "mai": "05", "Mai.": "05", "mai.": "05", 
        "Juni": "06", "juni": "06", "Jun": "06", "jun": "06", "Jun.": "06", "jun.": "06", 
        "Juli": "07", "juli": "07", "Jul": "07", "jul": "07", "Jul.": "07", "jul.": "07", 
        "August": "08", "august": "08", "Aug": "08", "aug": "08", "Aug.": "08", "aug.": "08", 
        "September": "09", "september": "09", "Sep": "09", "sep": "09", "Sep.": "09", "sep.": "09", 
        "Oktober": "10", "oktober": "10", "Okt": "10", "okt": "10", "Okt.": "10", "okt.": "10", 
        "November": "11", "november": "11", "Nov": "11", "nov": "11", "Nov.": "11", "nov.": "11", 
        "Desember": "12", "desember": "12", "Des": "12", "des": "12", "Des.": "12", "des.": "12",
        # Japanese
        "一月": "01", "二月": "02", "三月": "03", "四月": "04", "五月": "05",
        "六月": "06", "七月": "07", "八月": "08", "九月": "09", "十月": "10",
        "十一月": "11", "十二月": "12"
    }

    parts = input_date.split()
    
    day, month, year = "", "", ""
    for part in parts:
        if part in month_dict.keys():
            month = month_dict[part]
        elif len(part) == 4 and part.isdigit():
            year = part
        elif part.isdigit():
            day = part

    if day and month and year:
        numerical_date = f"{month}.{day}.{year}"
        return numerical_date
    else:
        return "Invalid date format"

# Tab for Date Translation
class DateTranslationTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        self.date_label = tk.Label(self, text="Enter a date in various formats (e.g., 'Month Day, Year', 'Day Month Year'):")
        self.date_label.pack(pady=10)

        self.date_entry = tk.Entry(self)
        self.date_entry.pack()

        self.translate_button = tk.Button(self, text="Translate", command=self.translate_button_click)
        self.translate_button.pack(pady=5)

        self.result_entry = tk.Entry(self)
        self.result_entry.pack(pady=10)

    def translate_button_click(self):
        input_date = self.date_entry.get()
        numerical_date = translate_date(input_date)
        
        if numerical_date != "Invalid date format":
            self.result_entry.delete(0, tk.END)
            self.result_entry.insert(0, f"{numerical_date}")
        else:
            self.result_entry.delete(0, tk.END)
            self.result_entry.insert(0, "Invalid input. Please use a valid format like 'January 1, 2022'.")



def copy_files(src, dst, file_types, update_status, update_progress, stop_flag, total_files):
    copied_files = 0
    for root, dirs, files in os.walk(src):
        if stop_flag.is_set():
            update_status("Copying stopped.")
            return

        dest_dir = os.path.join(dst, os.path.relpath(root, src))
        os.makedirs(dest_dir, exist_ok=True)

        for file in files:
            if any(file.endswith(ft) for ft in file_types):
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                shutil.copy(src_file, dest_file)
                update_status(f"Copied: {src_file}")

                # Update progress
                copied_files += 1
                progress = (copied_files / total_files) * 100
                update_progress(progress)

    update_status("Copy completed successfully.")

class FileCopy(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()
        self.file_types = {}
        self.checkboxes = []


    def create_widgets(self):

        self.src_button = tk.Button(self, text="Select Source Directory", command=self.choose_src)
        self.src_button.pack(side="top")

        self.dst_button = tk.Button(self, text="Select Destination Directory", command=self.choose_dst)
        self.dst_button.pack(side="top")

        self.copy_button = tk.Button(self, text="Start Copying", command=self.start_copy)
        self.copy_button.pack(side="top")

        self.status_label = tk.Label(self, text="", wraplength=300)
        self.status_label.pack(side="top")

        self.checkbox_frame = tk.Frame(self)
        self.checkbox_frame.pack()

    def scan_file_types(self, directory):
        # Clear existing checkboxes
        for checkbox in self.checkboxes:
            checkbox.destroy()
        self.checkboxes.clear()
        self.file_types.clear()

        # Scan the directory for file types
        row, col = 0, 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext and ext not in self.file_types:
                    self.file_types[ext] = tk.BooleanVar(value=False)
                    cb = tk.Checkbutton(self.checkbox_frame, text=ext, variable=self.file_types[ext])
                    cb.grid(row=row, column=col, sticky='w')
                    self.checkboxes.append(cb)
                    col += 1
                    if col >= 5:  # Move to next row after 5 checkboxes
                        col = 0
                        row += 1


    def start_copy(self):
        if hasattr(self, 'src_dir') and hasattr(self, 'dst_dir'):
            selected_file_types = [ext for ext, var in self.file_types.items() if var.get()]
            if not selected_file_types:
                messagebox.showerror("Error", "Please select at least one file type.")
                return

            # Count total files to be copied for progress calculation
            total_files = 0
            for root, dirs, files in os.walk(self.src_dir):
                total_files += sum(1 for file in files if any(file.endswith(ft) for ft in selected_file_types))
            
            # Create a threading event to stop the copying process
            self.stop_flag = threading.Event()

            # Start the copy_files function in a new thread
            copy_thread = threading.Thread(target=copy_files, args=(self.src_dir, self.dst_dir, selected_file_types, self.update_status, update_progress, self.stop_flag, total_files))
            copy_thread.start()
            
        else:
            messagebox.showerror("Error", "Please select both source and destination directories.")


    def stop_copy(self):
        # Set the stop flag to True
        if hasattr(self, 'stop_flag'):
            self.stop_flag.set()


    def choose_src(self):
        self.src_dir = filedialog.askdirectory(title='Choose source directory')
        if self.src_dir:
            self.status_label.config(text=f"Source: {self.src_dir}")
            self.scan_file_types(self.src_dir)


    def choose_dst(self):
        self.dst_dir = filedialog.askdirectory(title='Choose destination directory')
        self.status_label.config(text=f"Destination: {self.dst_dir}")

    def update_status(self, message):
        self.status_label.config(text=message)

class URLExtractionTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.dark_mode = False
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.create_widgets()

    def open_directory(self, event):
        index_at_click = self.output_text.index("@%s,%s" % (event.x, event.y))
        line, char = map(int, index_at_click.split('.'))
        
        line_start = f"{line}.0"
        line_end = f"{line}.end"
        
        line_text = self.output_text.get(line_start, line_end)
        
        # Assuming the directory path is enclosed within square brackets
        directory_pattern = re.compile(r'\[(.*?)\]')
        directory_matches = directory_pattern.findall(line_text)
        
        if directory_matches:
            directory_path = directory_matches[0]
            
            # Open the directory with the default file explorer
            if os.name == 'nt':  # For Windows
                os.startfile(directory_path)
            elif os.name == 'posix':  # For macOS and Linux
                subprocess.run(['open', directory_path])

    def open_url(self, event):
        index_at_click = self.output_text.index("@%s,%s" % (event.x, event.y))
        line, char = map(int, index_at_click.split('.'))
        
        line_start = f"{line}.0"
        line_end = f"{line}.end"
        
        line_text = self.output_text.get(line_start, line_end)
        urls = re.findall(self.url_pattern, line_text)
        
        if urls:
            webbrowser.open(urls[0])

    def separate_adjacent_urls(self, urls):
        separated_urls = []
        for url in urls:
            # Using a simple pattern to detect adjacent URLs by checking for "http(s)://"
            adjacent_urls = re.split(r'(?=http[s]?://)', url)
            separated_urls.extend(adjacent_urls)
        return separated_urls

    def extract_links_from_folders(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        self.output_text.delete('1.0', tk.END)

        # Calculate total number of files
        total_files = sum(1 for _, _, files in os.walk(folder_path) if any(file.endswith('.txt') for file in files))

        # Define a thread-safe update function
        def thread_safe_update(file_path, dirpath, urls, current_file, total_files):
            progress = (current_file / total_files) * 100
            update_progress(progress)
            self.output_text.insert(tk.END, f"From {os.path.basename(file_path)} in ", 'bold')
            self.output_text.insert(tk.END, f"[{dirpath}]", 'dir')
            self.output_text.insert(tk.END, ":\n", 'bold')
            for url in urls:
                self.output_text.insert(tk.END, url + '\n', 'link')
            self.output_text.insert(tk.END, "\n")

        # Start extraction in a new thread
        def start_extraction():
            current_file = 0
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    if filename.endswith('.txt'):
                        file_path = os.path.join(dirpath, filename)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            text = file.read()

                        urls = re.findall(self.url_pattern, text)
                        urls = self.separate_adjacent_urls(urls)  # Separate adjacent URLs
                        
                        current_file += 1
                        root.after(0, thread_safe_update, file_path, dirpath, urls, current_file, total_files)

            update_progress(100)  # Complete the progress

        threading.Thread(target=start_extraction).start()

    def clear_output(self):
        self.output_text.delete('1.0', tk.END)

    def export_links(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return

        text_to_export = self.output_text.get("1.0", tk.END)
        urls_to_export = re.findall(self.url_pattern, text_to_export)

        with open(file_path, "w", encoding='utf-8') as file:
            for url in urls_to_export:
                file.write(f"{url}\n")

    def create_widgets(self):
        # Button frame
        button_frame = tk.Frame(self)  # Define button_frame first
        button_frame.grid(row=0, column=0, sticky="ew")

        # Button to export the links
        export_button = tk.Button(button_frame, text="Export Links", command=self.export_links)
        export_button.pack(side="left", padx=10, pady=10)

        # Button to open the directory dialog
        open_button = tk.Button(button_frame, text="Open Folder", command=self.extract_links_from_folders)
        open_button.pack(side="left", padx=10, pady=10)

        # Button to clear the output
        clear_button = tk.Button(button_frame, text="Clear", command=self.clear_output)
        clear_button.pack(side="left", padx=10, pady=10)

        # Text widget to display extracted URLs
        self.output_text = tk.Text(self, wrap=tk.WORD)
        self.output_text.grid(row=1, column=0, sticky="nsew")

        # Scrollbar for text widget
        scrollbar = tk.Scrollbar(self, orient='vertical', command=self.output_text.yview)
        scrollbar.grid(row=1, column=1, sticky='ns')
        self.output_text['yscrollcommand'] = scrollbar.set

        # Configure hyperlink styling and click event
        self.output_text.tag_configure('link', foreground='blue', underline=True)
        self.output_text.tag_bind('link', '<ButtonRelease-1>', self.open_url)

        # Configure bold text
        self.output_text.tag_configure('bold', font=('TkDefaultFont', 10, 'bold'))

        # Configure directory link styling and click event
        self.output_text.tag_configure('dir', foreground='purple', underline=True)
        self.output_text.tag_bind('dir', '<ButtonRelease-1>', self.open_directory)

        # Make window resizable
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

def update_progress(value):
    progress_bar['value'] = value
    root.update_idletasks()

root = tk.Tk()
root.geometry("400x500")
root.title('Arachneia')

# Create a main frame
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Create a progress bar and place it at the top of the main frame
progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate', style="black.Horizontal.TProgressbar")
progress_bar.pack(side="top", fill=tk.X)

# Create a frame that will contain the tab control
tab_frame = tk.Frame(main_frame)
tab_frame.pack(fill=tk.BOTH, expand=True)

# Create a tab control (notebook) inside the tab frame
tab_control = ttk.Notebook(tab_frame)
png_copy_tab = FileCopy(tab_control)
date_translation_tab = DateTranslationTab(tab_control)
url_extraction_tab = URLExtractionTab(tab_control)

tab_control.add(png_copy_tab, text='Copy Files')
tab_control.add(date_translation_tab, text='Date Translation')
tab_control.add(url_extraction_tab, text='URL Extraction')
tab_control.pack(expand=1, fill=tk.BOTH)

style = ttk.Style(root)
style.theme_use('default')
style.configure("black.Horizontal.TProgressbar", background='#f1f1f1', troughcolor='#f1f1f1')


# update_progress(50)

# Run the application
root.mainloop()
