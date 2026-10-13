"""
Huffman Coding GUI Application
Provides a simple Tkinter interface for compressing and decompressing
text files using the backend Huffman algorithm.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Import core Huffman operations from backend.py
import backend

# Global variables to track current files and text state for lossless comparison
selected_input_file = ""
selected_huf_file = ""
last_compressed_original_text = ""


def format_char_for_display(char):
    """
    Converts special whitespace and invisible characters to readable labels
    so they display clearly in the Huffman code table.
    """
    if char == " ":
        return "<SPACE>"
    elif char == "\n":
        return "<NEWLINE>"
    elif char == "\t":
        return "<TAB>"
    elif char == "\r":
        return "<RETURN>"
    return repr(char) if not char.isprintable() else char


def browse_txt_file():
    """
    Opens a file dialog for the user to select a plain text (.txt) file,
    and loads its content into the original text preview area.
    """
    global selected_input_file
    file_path = filedialog.askopenfilename(
        title="Select a Text File to Compress",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not file_path:
        return

    if not file_path.lower().endswith(".txt"):
        messagebox.showerror("Invalid File", "Please select a valid .txt file.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        selected_input_file = file_path
        lbl_compress_path.config(text=os.path.basename(file_path))

        # Update the original text area
        txt_original.delete("1.0", tk.END)
        txt_original.insert(tk.END, content)

        # Clear previous compression results
        txt_encoded.delete("1.0", tk.END)
        for item in tree_codes.get_children():
            tree_codes.delete(item)
        lbl_stats.config(text="Original Size: - | Compressed Size: - | Space Saved: -")

    except Exception as err:
        messagebox.showerror("Read Error", f"Could not read the file:\n{err}")


def run_compression():
    """
    Performs compression on the selected text file:
    Generates Huffman codes, displays encoded bits, updates the frequency table,
    calculates compression stats, and saves the output .huf file.
    """
    global selected_input_file, last_compressed_original_text

    text_content = txt_original.get("1.0", tk.END).rstrip("\r\n")

    if not text_content:
        messagebox.showwarning("Empty Input", "The input text is empty. Nothing to compress!")
        return

    # Choose output location for .huf file
    default_name = "compressed.huf"
    if selected_input_file:
        base_name = os.path.splitext(selected_input_file)[0]
        default_name = base_name + ".huf"

    save_path = filedialog.asksaveasfilename(
        title="Save Compressed File As",
        initialfile=os.path.basename(default_name),
        defaultextension=".huf",
        filetypes=[("Huffman Compressed Files", "*.huf")]
    )
    if not save_path:
        return

    try:
        # Execute core Huffman logic from backend
        freq_table = backend.build_frequency_table(text_content)
        tree_root = backend.build_huffman_tree(freq_table)
        codes = backend.generate_codes(tree_root)
        bit_string = backend.encode_text(text_content, codes)
        stats = backend.get_stats(text_content, bit_string)

        # Save to .huf file format (JSON containing code table and bit string)
        import json
        payload = {"codes": codes, "bit_string": bit_string}
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        # Save state for verification during decompression
        last_compressed_original_text = text_content

        # 1. Display encoded bit string
        txt_encoded.delete("1.0", tk.END)
        txt_encoded.insert(tk.END, bit_string)

        # 2. Populate Huffman code table
        for item in tree_codes.get_children():
            tree_codes.delete(item)

        # Sort table by character frequency descending
        sorted_chars = sorted(codes.keys(), key=lambda ch: freq_table.get(ch, 0), reverse=True)
        for ch in sorted_chars:
            display_name = format_char_for_display(ch)
            freq = freq_table.get(ch, 0)
            code = codes[ch]
            tree_codes.insert("", tk.END, values=(display_name, freq, code))

        # 3. Update stats label
        stats_text = (
            f"Original Size: {stats['original_bits']} bits ({stats['original_chars']} chars)  |  "
            f"Compressed Size: {stats['compressed_bits']} bits  |  "
            f"Space Saved: {stats['saved_percentage']}%"
        )
        lbl_stats.config(text=stats_text, foreground="#006600")

        messagebox.showinfo("Success", f"File compressed and saved successfully to:\n{save_path}")

    except Exception as err:
        messagebox.showerror("Compression Error", f"An error occurred during compression:\n{err}")


def browse_huf_file():
    """
    Opens a file dialog for the user to select a compressed (.huf) file
    ready for decompression.
    """
    global selected_huf_file
    file_path = filedialog.askopenfilename(
        title="Select a Huffman (.huf) File",
        filetypes=[("Huffman Compressed Files", "*.huf"), ("All Files", "*.*")]
    )
    if not file_path:
        return

    if not file_path.lower().endswith(".huf"):
        messagebox.showerror("Invalid File", "Please select a valid .huf file.")
        return

    selected_huf_file = file_path
    lbl_decompress_path.config(text=os.path.basename(file_path))
    txt_restored.delete("1.0", tk.END)
    lbl_lossless_status.config(text="")


def run_decompression():
    """
    Performs decompression on the selected .huf file:
    Reconstructs the Huffman tree, decodes the bits back into text,
    saves the output .txt file, and verifies lossless integrity.
    """
    global selected_huf_file, last_compressed_original_text

    if not selected_huf_file:
        messagebox.showwarning("No File", "Please browse and select a .huf file first.")
        return

    default_name = "restored.txt"
    if selected_huf_file:
        base_name = os.path.splitext(selected_huf_file)[0]
        default_name = base_name + "_decompressed.txt"

    save_path = filedialog.asksaveasfilename(
        title="Save Restored Text File As",
        initialfile=os.path.basename(default_name),
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")]
    )
    if not save_path:
        return

    try:
        restored_text = backend.decompress_file(selected_huf_file, save_path)

        # Show restored text in preview
        txt_restored.delete("1.0", tk.END)
        txt_restored.insert(tk.END, restored_text)

        # Lossless integrity check
        if last_compressed_original_text:
            if restored_text == last_compressed_original_text:
                lbl_lossless_status.config(
                    text="Lossless check: PASSED (Restored text exactly matches original file!)",
                    foreground="#008800"
                )
            else:
                lbl_lossless_status.config(
                    text="Lossless check: FAILED (Restored text differs from original)",
                    foreground="#cc0000"
                )
        else:
            lbl_lossless_status.config(
                text=f"Decompression Completed: Saved to {os.path.basename(save_path)}",
                foreground="#0055aa"
            )

        messagebox.showinfo("Success", f"File decompressed successfully to:\n{save_path}")

    except Exception as err:
        messagebox.showerror("Decompression Error", f"Failed to decompress file:\n{err}")


# =========================================================================
# GUI SETUP (Tkinter window and widgets)
# =========================================================================
root = tk.Tk()
root.title("Huffman Text Compression & Decompression System")
root.geometry("900x700")
root.minsize(750, 550)

# Main tabbed interface
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# TAB 1: COMPRESSION
tab_compress = ttk.Frame(notebook)
notebook.add(tab_compress, text="Compress (.txt to .huf)")

# Tab 1 - File selection bar
frame_file_comp = ttk.Frame(tab_compress, padding=5)
frame_file_comp.pack(fill=tk.X)

btn_browse_txt = ttk.Button(frame_file_comp, text="Browse .txt File", command=browse_txt_file)
btn_browse_txt.pack(side=tk.LEFT, padx=5)

lbl_compress_path = ttk.Label(frame_file_comp, text="No file selected", font=("Arial", 9, "italic"))
lbl_compress_path.pack(side=tk.LEFT, padx=5)

btn_do_compress = ttk.Button(frame_file_comp, text="Compress & Save (.huf)", command=run_compression)
btn_do_compress.pack(side=tk.RIGHT, padx=5)

# Tab 1 - PanedWindow split for Original Text and Encoded Bit String
pane_texts = ttk.PanedWindow(tab_compress, orient=tk.HORIZONTAL)
pane_texts.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Left box: Original Text
frame_orig = ttk.LabelFrame(pane_texts, text="Original Text Preview", padding=5)
pane_texts.add(frame_orig, weight=1)

txt_original = tk.Text(frame_orig, wrap=tk.WORD, height=10, font=("Consolas", 10))
scroll_orig = ttk.Scrollbar(frame_orig, orient=tk.VERTICAL, command=txt_original.yview)
txt_original.config(yscrollcommand=scroll_orig.set)
txt_original.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_orig.pack(side=tk.RIGHT, fill=tk.Y)

# Right box: Encoded Bit String
frame_enc = ttk.LabelFrame(pane_texts, text="Encoded Bit String (0s and 1s)", padding=5)
pane_texts.add(frame_enc, weight=1)

txt_encoded = tk.Text(frame_enc, wrap=tk.CHAR, height=10, font=("Consolas", 10), foreground="#003366")
scroll_enc = ttk.Scrollbar(frame_enc, orient=tk.VERTICAL, command=txt_encoded.yview)
txt_encoded.config(yscrollcommand=scroll_enc.set)
txt_encoded.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_enc.pack(side=tk.RIGHT, fill=tk.Y)

# Tab 1 - Huffman Code Table (Treeview)
frame_table = ttk.LabelFrame(tab_compress, text="Huffman Code Table", padding=5)
frame_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

tree_columns = ("char", "freq", "code")
tree_codes = ttk.Treeview(frame_table, columns=tree_columns, show="headings", height=7)
tree_codes.heading("char", text="Character")
tree_codes.heading("freq", text="Frequency")
tree_codes.heading("code", text="Huffman Binary Code")

tree_codes.column("char", width=120, anchor=tk.CENTER)
tree_codes.column("freq", width=100, anchor=tk.CENTER)
tree_codes.column("code", width=250, anchor=tk.W)

scroll_table = ttk.Scrollbar(frame_table, orient=tk.VERTICAL, command=tree_codes.yview)
tree_codes.config(yscrollcommand=scroll_table.set)
tree_codes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_table.pack(side=tk.RIGHT, fill=tk.Y)

# Tab 1 - Statistics Bar
lbl_stats = ttk.Label(
    tab_compress,
    text="Original Size: - | Compressed Size: - | Space Saved: -",
    font=("Arial", 10, "bold"),
    padding=8
)
lbl_stats.pack(fill=tk.X)


# TAB 2: DECOMPRESSION
tab_decompress = ttk.Frame(notebook)
notebook.add(tab_decompress, text="Decompress (.huf to .txt)")

# Tab 2 - File selection bar
frame_file_decomp = ttk.Frame(tab_decompress, padding=5)
frame_file_decomp.pack(fill=tk.X)

btn_browse_huf = ttk.Button(frame_file_decomp, text="Browse .huf File", command=browse_huf_file)
btn_browse_huf.pack(side=tk.LEFT, padx=5)

lbl_decompress_path = ttk.Label(frame_file_decomp, text="No file selected", font=("Arial", 9, "italic"))
lbl_decompress_path.pack(side=tk.LEFT, padx=5)

btn_do_decompress = ttk.Button(frame_file_decomp, text="Decompress & Save (.txt)", command=run_decompression)
btn_do_decompress.pack(side=tk.RIGHT, padx=5)

# Tab 2 - Lossless Verification Status
lbl_lossless_status = ttk.Label(tab_decompress, text="", font=("Arial", 10, "bold"), padding=5)
lbl_lossless_status.pack(fill=tk.X, padx=5)

# Tab 2 - Restored Text Box
frame_restored = ttk.LabelFrame(tab_decompress, text="Restored Plain Text", padding=5)
frame_restored.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

txt_restored = tk.Text(frame_restored, wrap=tk.WORD, font=("Consolas", 10))
scroll_restored = ttk.Scrollbar(frame_restored, orient=tk.VERTICAL, command=txt_restored.yview)
txt_restored.config(yscrollcommand=scroll_restored.set)
txt_restored.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_restored.pack(side=tk.RIGHT, fill=tk.Y)

# Start Tkinter event loop
if __name__ == "__main__":
    root.mainloop()
