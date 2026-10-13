# Huffman-Based Text Compression and Decompression System

A lightweight, demo-ready **Huffman Coding** application built with Python 3 and Tkinter for a B.Tech Information Technology mid-semester project review.

---

## 1. What is Huffman Coding?
Huffman coding is a fundamental **greedy, lossless data compression algorithm**. Instead of using fixed 8-bit ASCII representations for every character, it assigns **variable-length binary prefix codes** based on character frequency:
- Characters that appear **frequently** receive **shorter** binary codes (e.g., 2–3 bits).
- Characters that appear **rarely** receive **longer** binary codes (e.g., 6–8 bits).
- Because no code is a prefix of any other code, the encoded bit sequence can be uniquely decoded without ambiguity.

---

## 2. Project Architecture & File Connections

The project follows a clean separation of concerns:

```
huffman_project/
│
├── backend.py      # Core data structures and algorithmic operations (no UI code)
├── frontend.py     # Clean Tkinter GUI (calls backend functions)
├── sample.txt      # Repetitive sample text file for viva/lab demonstration
└── README.md       # Project documentation and viva preparation guide
```

### How the Files Connect:
- `backend.py` defines the `Node` class and all Huffman logic (`build_frequency_table`, `build_huffman_tree`, `generate_codes`, `encode_text`, `decode_text`, `compress_file`, `decompress_file`, `get_stats`).
- `frontend.py` imports `backend.py` and provides a graphical interface. When the user clicks **Compress**, it passes the text to `backend.compress_file()`, extracts the generated codes, displays the bit string and code table, and saves a `.huf` file.
- When the user clicks **Decompress**, `frontend.py` passes the `.huf` file to `backend.decompress_file()`, which reconstructs the tree, decodes the bit stream back to text, and confirms lossless data integrity.

---

## 3. Project Status: ~70% Complete (Mid-Semester Milestone)

This project has been intentionally scoped to **~70% completion** for the mid-semester evaluation:
- The **core algorithmic foundation and GUI are 100% complete, fully working, and demo-ready**.
- Advanced industrial-grade optimizations and multi-format support are outlined as **future work** for the final-semester submission.

### Implemented Features (Working & Demo-Ready)
- [x] **Character Frequency Counter:** Generates frequency dictionaries using `collections.Counter`.
- [x] **Optimal Huffman Tree Construction:** Built using Python's standard `heapq` (min-heap) with \(O(N \log N)\) efficiency.
- [x] **Recursive Prefix Code Generation:** DFS traversal that assigns '0' for left branches and '1' for right branches.
- [x] **Tree Traversal Decoding:** Restores the exact text character-by-character by walking the reconstructed tree.
- [x] **File Compression & Decompression:** Reads `.txt` files and outputs `.huf` files (storing the code table and bit string), and vice-versa.
- [x] **Statistical Analytics:** Computes original size in bits, compressed size in bits, and percentage saved (typically 40%–50% savings).
- [x] **Edge Case Handling:** Handles empty files and single-character strings (`"AAAAA"`) safely.
- [x] **Interactive Tkinter GUI:** Tabbed layout for compression and decompression with file browsers, live preview, scrollable code table, and a lossless verification check.

### Planned Future Work (Remaining ~30% for Final Review)
- [ ] **True Bit-Packing / Byte-Level I/O:** Currently, the encoded bit sequence is stored as text characters (`'0'` and `'1'`) inside a JSON container for educational transparency. In the final phase, bits will be packed 8-at-a-time into binary bytes using `bytearray` and bitwise operations (`<<`, `|`) to reduce actual disk file size.
- [ ] **Canonical Huffman Coding / Compact Header:** Storing only code lengths rather than the full JSON dictionary in the file header to minimize metadata overhead.
- [ ] **Graphical Tree Visualizer:** Using a Canvas widget to draw the binary tree diagram dynamically during compression.
- [ ] **Binary & Multi-File Support:** Extending compression to images (`.png`), PDFs, and audio files.
- [ ] **Adaptive (Dynamic) Huffman Coding:** Updating tree weights dynamically on-the-fly (FGK or Vitter algorithm) without requiring a two-pass scan.

---

## 4. How to Run

### Prerequisites
- Python 3.8+ (Uses only built-in standard library modules: `tkinter`, `heapq`, `os`, `collections`, `json`).
- No external packages (`pip`) required!

### Step 1: Run Backend Self-Test (Verification)
Verify that all algorithms and edge cases pass:
```bash
python backend.py
```
*Expected Output:* Displays test runs for standard text, single character input, and empty string, ending with `All backend tests completed successfully!`.

### Step 2: Launch the GUI Application
```bash
python frontend.py
```

### Step 3: Demo Walkthrough
1. **Compress Tab:**
   - Click **Browse .txt File** and choose `sample.txt`.
   - Click **Compress & Save (.huf)** and choose an output location (e.g. `sample.huf`).
   - Observe the generated binary bit string, the character frequency code table, and the statistics panel (~44% space saved).
2. **Decompress Tab:**
   - Switch to the **Decompress** tab.
   - Click **Browse .huf File** and choose the `sample.huf` file created in step 1.
   - Click **Decompress & Save (.txt)** and save as `sample_restored.txt`.
   - Notice the green verification banner: **`Lossless check: PASSED`**.

---

## 5. Viva Q&A Guide (Mid-Semester Review Preparation)

### Q1: Why do we use a Min-Heap (Priority Queue) to build the Huffman Tree?
**Answer:** Huffman's greedy algorithm requires us to repeatedly pick the two nodes with the lowest frequencies and merge them. A min-heap (`heapq`) provides \(O(1)\) lookup and \(O(\log N)\) extraction/insertion, allowing the entire tree to be built efficiently in \(O(N \log N)\) time.

### Q2: What is the "Prefix Property" (Prefix-Free Code), and why is it essential?
**Answer:** A code system has the prefix property if no character's binary code is a prefix (starting sequence) of any other character's code. For example, if `'e'` is `01`, no other character can start with `01`. This property ensures that the encoded bit stream can be decoded deterministically without delimiters or spaces between characters.

### Q3: What is the Time and Space Complexity of Huffman Coding?
**Answer:**
- **Time Complexity:**
  - Counting frequencies: \(O(L)\), where \(L\) is the total length of the text.
  - Building the tree: \(O(N \log N)\), where \(N\) is the number of *unique* characters (at most 256 for standard ASCII).
  - Encoding and Decoding: \(O(L)\).
- **Space Complexity:** \(O(N)\) to store the tree nodes and code dictionary.

### Q4: Why is Huffman coding classified as "Lossless" compression?
**Answer:** Lossless compression algorithms preserve 100% of the original information. When the bit stream is decoded using the exact tree or code table, the reconstructed text is identical bit-for-bit to the input text, without any data degradation (unlike lossy algorithms used for JPEG or MP3).

### Q5: What is the theoretical compression ratio achieved here?
**Answer:** In standard ASCII, each character uses 8 bits. With Huffman coding, high-frequency characters (like spaces and vowels) use only 2 to 4 bits, while rare characters use 6 to 8 bits. For natural English text, the average code length drops to around 4.5 bits per character, yielding a theoretical storage saving of **40% to 50%**.

### Q6: What is the difference between Static and Adaptive Huffman Coding?
**Answer:**
- **Static Huffman (Implemented here):** Requires two passes over the data—the first pass counts character frequencies to build the tree, and the second pass encodes the data. The tree/code table must be stored in the file.
- **Adaptive Huffman:** Encodes data in a single pass, updating the tree dynamically as characters are read.

### Q7: What is the main limitation of this ~70% mid-semester prototype?
**Answer:** For educational clarity, the prototype writes the bit string as ASCII characters (`'0'` and `'1'`) in a JSON file rather than packing every 8 bits into a physical 1-byte binary structure. The algorithm calculates the true compressed bit size accurately, and true binary bit-packing is part of the final-semester planned work.
