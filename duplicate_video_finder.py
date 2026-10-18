import os
import re
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv",
    ".webm", ".m4v", ".mpeg", ".mpg", ".ts", ".mts",
    ".m2ts", ".3gp", ".vob"
}

COPY_SUFFIX = re.compile(r"\\s*\\(\\s*\\d+\\s*\\)\\s*$")


def normalize_name(filename):
    stem = Path(filename).stem
    stem = COPY_SUFFIX.sub("", stem)
    return stem.strip().casefold()


def is_numbered_copy(filename):
    return bool(COPY_SUFFIX.search(Path(filename).stem))


class DuplicateVideoFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Video Finder")
        self.root.geometry("1150x650")
        self.root.minsize(850, 450)

        self.folder_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Select a folder to begin.")

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Folder:").pack(side="left")
        ttk.Entry(top, textvariable=self.folder_var).pack(
            side="left", fill="x", expand=True, padx=8
        )
        ttk.Button(top, text="Browse", command=self.choose_folder).pack(
            side="left"
        )
        ttk.Button(
            top, text="Find Duplicates", command=self.find_duplicates
        ).pack(side="left", padx=(8, 0))

        columns = ("group", "filename", "size", "path")
        table_frame = ttk.Frame(root, padding=(10, 0, 10, 0))
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            selectmode="extended"
        )
        self.tree.heading("group", text="Duplicate Group")
        self.tree.heading("filename", text="Copy Filename")
        self.tree.heading("size", text="Size")
        self.tree.heading("path", text="Full Path")

        self.tree.column("group", width=200, anchor="w")
        self.tree.column("filename", width=270, anchor="w")
        self.tree.column("size", width=100, anchor="e")
        self.tree.column("path", width=550, anchor="w")

        scrollbar_y = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        scrollbar_x = ttk.Scrollbar(
            root, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        scrollbar_x.pack(fill="x", padx=10)

        bottom = ttk.Frame(root, padding=10)
        bottom.pack(fill="x")

        ttk.Button(
            bottom, text="Open File Location",
            command=self.open_file_location
        ).pack(side="left")
        ttk.Button(
            bottom, text="Delete Selected",
            command=self.delete_selected
        ).pack(side="left", padx=6)
        ttk.Button(
            bottom, text="Delete All Duplicates",
            command=self.delete_all_duplicates
        ).pack(side="left", padx=6)
        ttk.Label(bottom, textvariable=self.status_var).pack(
            side="left", padx=10
        )

    def choose_folder(self):
        folder = filedialog.askdirectory(
            title="Select folder containing videos"
        )
        if folder:
            self.folder_var.set(folder)

    def find_duplicates(self):
        folder = self.folder_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror(
                "Folder Required", "Please select a valid folder first."
            )
            return

        self.tree.delete(*self.tree.get_children())
        self.status_var.set("Scanning videos...")
        self.root.update_idletasks()

        groups = {}
        scanned = 0
        errors = 0

        for current_folder, _, filenames in os.walk(folder):
            for filename in filenames:
                path = os.path.join(current_folder, filename)
                if Path(filename).suffix.casefold() not in VIDEO_EXTENSIONS:
                    continue

                scanned += 1
                try:
                    size = os.path.getsize(path)
                except OSError:
                    errors += 1
                    continue

                key = normalize_name(filename)
                groups.setdefault(key, []).append({
                    "filename": filename,
                    "path": path,
                    "size": size,
                    "is_copy": is_numbered_copy(filename)
                })

        duplicate_groups = 0
        copies_shown = 0

        for key, files in sorted(groups.items()):
            copies = [item for item in files if item["is_copy"]]
            originals = [item for item in files if not item["is_copy"]]

            # Display numbered copies only, never the original.
            if copies and (originals or len(copies) > 1):
                duplicate_groups += 1
                for item in sorted(
                    copies, key=lambda value: value["filename"].casefold()
                ):
                    self.tree.insert(
                        "", "end",
                        values=(
                            key, item["filename"],
                            self.format_size(item["size"]), item["path"]
                        )
                    )
                    copies_shown += 1

        self.status_var.set(
            f"Scanned: {scanned} | Groups: {duplicate_groups} | "
            f"Copies: {copies_shown} | Errors: {errors}"
        )
        if copies_shown == 0:
            messagebox.showinfo(
                "Scan Complete", "No numbered duplicate copies were found."
            )

    @staticmethod
    def format_size(size):
        value = float(size)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                return f"{value:.2f} {unit}"
            value /= 1024
        return f"{value:.2f} TB"

    def open_file_location(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Nothing Selected", "Select a video first."
            )
            return

        path = self.tree.item(selected[0], "values")[3]
        if os.path.isfile(path):
            try:
                os.startfile(os.path.dirname(path))
            except OSError as error:
                messagebox.showerror("Could Not Open Folder", str(error))
        else:
            messagebox.showwarning(
                "File Not Found",
                "This file may have already been moved or deleted."
            )

    def get_eligible_rows(self, row_ids):
        eligible = []
        for item_id in row_ids:
            values = self.tree.item(item_id, "values")
            if len(values) < 4:
                continue

            path = values[3]
            filename = os.path.basename(path)
            if (
                Path(filename).suffix.casefold() in VIDEO_EXTENSIONS
                and is_numbered_copy(filename)
            ):
                eligible.append((item_id, path))
        return eligible

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Nothing Selected", "Select one or more duplicate copies."
            )
            return

        eligible = self.get_eligible_rows(selected)
        if not eligible:
            messagebox.showwarning(
                "No Eligible Copies", "No numbered video copies were selected."
            )
            return

        confirmed = messagebox.askyesno(
            "Confirm Permanent Deletion",
            f"Permanently delete {len(eligible)} selected copy/copies?\\n\\n"
            "Files will NOT go to the Recycle Bin. This may not be recoverable."
        )
        if confirmed:
            self.delete_paths(eligible)

    def delete_all_duplicates(self):
        rows = self.tree.get_children()
        if not rows:
            messagebox.showinfo(
                "No Duplicates", "There are no listed duplicate copies to delete."
            )
            return

        eligible = self.get_eligible_rows(rows)
        if not eligible:
            messagebox.showinfo(
                "No Eligible Copies",
                "No numbered duplicate copies were found in the list."
            )
            return

        confirmed = messagebox.askyesno(
            "Confirm Delete All",
            f"PERMANENTLY delete all {len(eligible)} listed copies?\\n\\n"
            "Original files without numbered suffixes are protected.\\n"
            "Files will NOT go to the Recycle Bin. This may not be recoverable."
        )
        if confirmed:
            self.delete_paths(eligible)

    def delete_paths(self, eligible):
        deleted = 0
        failed = 0

        for item_id, path in eligible:
            filename = os.path.basename(path)

            # Recheck extension and numbered suffix before each deletion.
            if (
                Path(filename).suffix.casefold() not in VIDEO_EXTENSIONS
                or not is_numbered_copy(filename)
            ):
                failed += 1
                continue

            try:
                if os.path.isfile(path):
                    os.remove(path)
                    deleted += 1
                self.tree.delete(item_id)
            except OSError:
                failed += 1

        self.status_var.set(
            f"Deletion complete | Deleted: {deleted} | Failed: {failed}"
        )
        messagebox.showinfo(
            "Deletion Results", f"Deleted: {deleted}\\nFailed: {failed}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateVideoFinder(root)
    root.mainloop()
