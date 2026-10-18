import os
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "Duplicate Video Finder"
VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
    ".m4v", ".mpeg", ".mpg", ".ts", ".mts", ".m2ts", ".3gp"
}

BG = "#10131a"
PANEL = "#191e29"
PANEL_2 = "#202737"
TEXT = "#eef2ff"
MUTED = "#9aa6bd"
ACCENT = "#8b5cf6"
ACCENT_HOVER = "#7544e8"
TEAL = "#2dd4bf"
RED = "#fb7185"
BORDER = "#30394b"


def format_size(size):
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024


def duplicate_base(filename):
    """Return normalized original name only for files ending in (2), (3), etc."""
    stem, ext = os.path.splitext(filename)
    match = re.match(r"^(.*?)\s*\((\d+)\)$", stem)
    if not match or int(match.group(2)) < 2:
        return None
    original_stem = match.group(1).strip()
    if not original_stem:
        return None
    return (original_stem.casefold(), ext.casefold())


class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1050x700")
        self.root.minsize(800, 520)
        self.root.configure(bg=BG)

        self.folder = ""
        self.duplicate_paths = []
        self.path_by_item = {}

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=PANEL,
            foreground=TEXT,
            fieldbackground=PANEL,
            rowheight=34,
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=PANEL_2,
            foreground=TEXT,
            relief="flat",
            font=("Segoe UI Semibold", 10)
        )
        style.map("Treeview", background=[("selected", "#453078")],
                  foreground=[("selected", "#ffffff")])
        style.configure(
            "Vertical.TScrollbar",
            background=PANEL_2,
            troughcolor=BG,
            bordercolor=BG,
            arrowcolor=TEXT
        )

    def _button(self, parent, text, command, bg=ACCENT, fg="white", width=None):
        button = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=ACCENT_HOVER,
            activeforeground="white", relief="flat", bd=0,
            font=("Segoe UI Semibold", 10), padx=16, pady=10,
            cursor="hand2"
        )
        if width:
            button.configure(width=width)
        return button

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=26, pady=(22, 12))

        tk.Label(
            header, text="Duplicate Video Finder", bg=BG, fg=TEXT,
            font=("Segoe UI Semibold", 22)
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Find numbered copies like  movie (2).mkv  without listing the original.",
            bg=BG, fg=MUTED, font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        folder_card = tk.Frame(self.root, bg=PANEL, highlightbackground=BORDER,
                               highlightthickness=1)
        folder_card.pack(fill="x", padx=26, pady=8)

        folder_row = tk.Frame(folder_card, bg=PANEL)
        folder_row.pack(fill="x", padx=16, pady=14)
        self.folder_label = tk.Label(
            folder_row, text="No folder selected", bg=PANEL, fg=MUTED,
            font=("Segoe UI", 10), anchor="w"
        )
        self.folder_label.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self._button(folder_row, "Choose Folder", self.choose_folder).pack(side="right")
        self._button(folder_row, "Scan Folder", self.start_scan, bg="#0f9f91").pack(
            side="right", padx=(0, 8)
        )

        stats = tk.Frame(self.root, bg=BG)
        stats.pack(fill="x", padx=26, pady=(8, 12))
        self.count_value = self._stat_card(stats, "DUPLICATE COPIES", "0", 0)
        self.size_value = self._stat_card(stats, "TOTAL SIZE", "0 B", 1)
        self.status_value = self._stat_card(stats, "STATUS", "Ready", 2)

        table_frame = tk.Frame(self.root, bg=PANEL, highlightbackground=BORDER,
                               highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=26, pady=(0, 12))

        columns = ("name", "size", "folder")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                 selectmode="extended")
        self.tree.heading("name", text="Duplicate file")
        self.tree.heading("size", text="Size")
        self.tree.heading("folder", text="Location")
        self.tree.column("name", width=300, minwidth=180, anchor="w")
        self.tree.column("size", width=100, minwidth=80, anchor="e")
        self.tree.column("folder", width=500, minwidth=180, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=26, pady=(0, 22))
        self._button(footer, "Select All", self.select_all, bg=PANEL_2).pack(side="left")
        self._button(footer, "Delete Selected", self.delete_selected, bg="#b93855").pack(
            side="right"
        )
        self._button(footer, "Delete All Duplicates", self.delete_all, bg="#dc3545").pack(
            side="right", padx=(0, 8)
        )
        tk.Label(
            self.root, text="Warning: deletion is permanent (not sent to Recycle Bin).",
            bg=BG, fg=RED, font=("Segoe UI", 9)
        ).pack(anchor="w", padx=28, pady=(0, 10))

    def _stat_card(self, parent, label, value, column):
        card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0))
        parent.grid_columnconfigure(column, weight=1)
        tk.Label(card, text=label, bg=PANEL, fg=MUTED,
                 font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=14, pady=(11, 2))
        value_label = tk.Label(card, text=value, bg=PANEL, fg=TEAL,
                               font=("Segoe UI Semibold", 16))
        value_label.pack(anchor="w", padx=14, pady=(0, 11))
        return value_label

    def choose_folder(self):
        selected = filedialog.askdirectory(title="Choose folder to scan")
        if selected:
            self.folder = selected
            self.folder_label.config(text=selected, fg=TEXT)
            self.status_value.config(text="Ready", fg=TEAL)

    def start_scan(self):
        if not self.folder:
            messagebox.showinfo("Choose a folder", "Please choose a folder first.")
            return
        self.status_value.config(text="Scanning…", fg="#fbbf24")
        self._button_scan_state(False)
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _button_scan_state(self, enabled):
        # Keep UI responsive while scanning; status is the visible progress indicator.
        pass

    def _scan_worker(self):
        try:
            all_videos = []
            for current, dirs, files in os.walk(self.folder):
                dirs[:] = [d for d in dirs if d not in {"$RECYCLE.BIN", "System Volume Information"}]
                for filename in files:
                    if os.path.splitext(filename)[1].casefold() in VIDEO_EXTENSIONS:
                        full_path = os.path.join(current, filename)
                        try:
                            size = os.path.getsize(full_path)
                        except OSError:
                            size = 0
                        all_videos.append((full_path, filename, size))

            names = {}
            for path, filename, size in all_videos:
                names.setdefault((os.path.dirname(path).casefold(), filename.casefold()), []).append(
                    (path, filename, size)
                )

            # Only list numbered copies when the matching original exists in the same folder.
            duplicates = []
            for path, filename, size in all_videos:
                base = duplicate_base(filename)
                if not base:
                    continue
                original_stem, ext = base
                original_name = (original_stem + ext).casefold()
                folder_key = os.path.dirname(path).casefold()
                if (folder_key, original_name) in names:
                    duplicates.append((path, filename, size))

            self.root.after(0, lambda: self._show_results(duplicates))
        except Exception as exc:
            self.root.after(0, lambda error=str(exc): self._scan_error(error))

    def _scan_error(self, error):
        self.status_value.config(text="Error", fg=RED)
        self._button_scan_state(True)
        messagebox.showerror("Scan failed", f"Could not scan this folder.\n\n{error}")

    def _show_results(self, duplicates):
        self.duplicate_paths = [item[0] for item in duplicates]
        self.path_by_item.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_size = 0
        for path, filename, size in duplicates:
            item_id = self.tree.insert(
                "", "end", values=(filename, format_size(size), os.path.dirname(path))
            )
            self.path_by_item[item_id] = path
            total_size += size

        self.count_value.config(text=str(len(duplicates)))
        self.size_value.config(text=format_size(total_size))
        self.status_value.config(text="Scan complete", fg=TEAL)
        self._button_scan_state(True)

    def select_all(self):
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children)

    def _delete_paths(self, paths):
        if not paths:
            messagebox.showinfo("Nothing selected", "There are no duplicate files to delete.")
            return

        noun = "file" if len(paths) == 1 else "files"
        confirmed = messagebox.askyesno(
            "Confirm permanent deletion",
            f"Permanently delete {len(paths)} duplicate {noun}?\n\n"
            "This cannot be undone and files will not go to the Recycle Bin."
        )
        if not confirmed:
            return

        deleted = 0
        failed = []
        for path in paths:
            try:
                os.remove(path)
                deleted += 1
            except OSError as exc:
                failed.append(f"{path}\n  {exc}")

        self._refresh_after_delete()
        message = f"Deleted {deleted} file(s)."
        if failed:
            message += f"\n\nCould not delete {len(failed)} file(s):\n" + "\n".join(failed[:5])
        messagebox.showinfo("Deletion finished", message)

    def delete_selected(self):
        selected = self.tree.selection()
        paths = [self.path_by_item[item] for item in selected if item in self.path_by_item]
        self._delete_paths(paths)

    def delete_all(self):
        self._delete_paths(list(self.duplicate_paths))

    def _refresh_after_delete(self):
        # Re-scan so the table and size stats reflect files that still exist.
        self.start_scan()


def main():
    root = tk.Tk()
    DuplicateFinderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
