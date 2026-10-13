"""
Huffman Coding Backend Logic
This module contains the core data structures and algorithmic steps
for Huffman encoding, decoding, file compression, and decompression.
"""

import os
import json
import heapq
from collections import Counter


class Node:
    """
    A simple node class representing an element in the Huffman tree.
    Each node stores a character, its frequency, and left/right children.
    """
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    # Allows heapq to compare nodes based on frequency
    def __lt__(self, other):
        return self.freq < other.freq


# Count how many times each character appears in the text
def build_frequency_table(text):
    """
    Takes a string of text and returns a dictionary mapping
    each unique character to its frequency count.
    """
    return dict(Counter(text))


# Build the optimal Huffman binary tree from character frequencies using a min-heap
def build_huffman_tree(freq_table):
    """
    Takes a frequency dictionary, inserts all characters into a min-heap,
    and repeatedly merges the two lowest-frequency nodes until only the root remains.
    """
    if not freq_table:
        return None

    # Step 1: Create a leaf node for each character and push into min-heap
    heap = []
    for char, freq in freq_table.items():
        heapq.heappush(heap, Node(char, freq))

    # Edge case: If there is only one unique character in the text
    if len(heap) == 1:
        single_node = heapq.heappop(heap)
        root = Node(None, single_node.freq, left=single_node, right=None)
        return root

    # Step 2: Merge the two smallest nodes until one tree remains
    while len(heap) > 1:
        left_child = heapq.heappop(heap)
        right_child = heapq.heappop(heap)

        parent = Node(
            char=None,
            freq=left_child.freq + right_child.freq,
            left=left_child,
            right=right_child
        )
        heapq.heappush(heap, parent)

    return heap[0]


# Traverse the tree recursively to generate variable-length binary prefix codes
def generate_codes(root):
    """
    Recursively walks the Huffman tree from the root to every leaf.
    Assigns '0' for every left branch and '1' for every right branch.
    Returns a dictionary mapping characters to binary string codes.
    """
    if not root:
        return {}

    codes = {}

    def _traverse(node, current_code):
        if node is None:
            return

        # Leaf node found (it holds an actual character)
        if node.char is not None:
            # If text had only one character, ensure code is not empty
            codes[node.char] = current_code if current_code else "0"
            return

        _traverse(node.left, current_code + "0")
        _traverse(node.right, current_code + "1")

    _traverse(root, "")
    return codes


# Reconstruct a Huffman tree structure from a code table
def rebuild_tree_from_codes(codes):
    """
    Rebuilds the binary tree using the code dictionary.
    Used during decompression so we can decode by walking the tree.
    """
    if not codes:
        return None

    root = Node(None, 0)
    for char, code in codes.items():
        current = root
        for bit in code:
            if bit == "0":
                if current.left is None:
                    current.left = Node(None, 0)
                current = current.left
            else:
                if current.right is None:
                    current.right = Node(None, 0)
                current = current.right
        current.char = char

    return root


# Replace each character in the original text with its Huffman binary code
def encode_text(text, codes):
    """
    Takes the original input text and the code table dictionary,
    and returns the complete concatenated bit string.
    """
    if not text:
        return ""
    return "".join(codes[char] for char in text)


# Walk down the Huffman tree bit-by-bit to restore the original characters
def decode_text(bit_string, root):
    """
    Takes an encoded bit string and the root of the Huffman tree.
    Follows '0' left and '1' right until reaching a leaf character,
    then repeats from the root to decode the entire text.
    """
    if not root or not bit_string:
        return ""

    # Special case: Root is itself a leaf (single character text)
    if root.char is not None and root.left is None and root.right is None:
        return root.char * len(bit_string)

    decoded_chars = []
    current = root

    for bit in bit_string:
        if bit == "0":
            current = current.left
        elif bit == "1":
            current = current.right

        if current is None:
            current = root
            continue

        # When a leaf node is reached, record the character and reset to root
        if current.char is not None:
            decoded_chars.append(current.char)
            current = root

    return "".join(decoded_chars)


# Calculate size and compression efficiency statistics
def get_stats(original_text, bit_string):
    """
    Calculates original size in bits (8 bits per character),
    compressed size in bits, and the percentage of storage saved.
    """
    original_bits = len(original_text) * 8
    compressed_bits = len(bit_string)

    if original_bits > 0:
        savings = ((original_bits - compressed_bits) / original_bits) * 100
    else:
        savings = 0.0

    return {
        "original_chars": len(original_text),
        "original_bits": original_bits,
        "compressed_bits": compressed_bits,
        "saved_percentage": round(savings, 2)
    }


# Compress a text file and save the encoded data into a .huf file
def compress_file(input_path, output_path):
    """
    Reads a plain text file, computes Huffman codes, encodes the text,
    and saves the code table and bit string as a JSON structure in a .huf file.
    Returns (stats, codes, bit_string, original_text).
    """
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    freq_table = build_frequency_table(text)
    root = build_huffman_tree(freq_table)
    codes = generate_codes(root)
    bit_string = encode_text(text, codes)
    stats = get_stats(text, bit_string)

    payload = {
        "codes": codes,
        "bit_string": bit_string
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return stats, codes, bit_string, text


# Decompress a .huf file back into a readable plain text file
def decompress_file(huf_path, output_path):
    """
    Reads a .huf file, reconstructs the Huffman tree from stored codes,
    decodes the bit string by traversing the tree, and writes the restored text to output_path.
    Returns the restored text.
    """
    with open(huf_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    codes = payload.get("codes", {})
    bit_string = payload.get("bit_string", "")

    root = rebuild_tree_from_codes(codes)
    restored_text = decode_text(bit_string, root)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(restored_text)

    return restored_text


# Self-contained test to verify compression and decompression
if __name__ == "__main__":
    print("=" * 60)
    print("Running Backend Verification Tests")
    print("=" * 60)

    # Test 1: Standard sentence
    sample_sentence = "B.Tech IT Huffman Mini Project Demonstration - Lossless Data Compression!"
    freqs = build_frequency_table(sample_sentence)
    tree_root = build_huffman_tree(freqs)
    code_map = generate_codes(tree_root)
    encoded = encode_text(sample_sentence, code_map)
    reconstructed_root = rebuild_tree_from_codes(code_map)
    decoded = decode_text(encoded, reconstructed_root)
    stats = get_stats(sample_sentence, encoded)

    print(f"Original Text: {sample_sentence}")
    print(f"Encoded Bits Sample (first 50 bits): {encoded[:50]}...")
    print(f"Decoded Text:  {decoded}")
    print(f"Original Bits: {stats['original_bits']}, Compressed Bits: {stats['compressed_bits']}")
    print(f"Space Saved:   {stats['saved_percentage']}%")
    assert sample_sentence == decoded, "Test 1 Failed: Decoded text does not match original!"
    print("Test 1 (Standard Sentence): PASSED\n")

    # Test 2: Single unique character edge case
    single_char_text = "AAAAAAA"
    freqs_single = build_frequency_table(single_char_text)
    tree_single = build_huffman_tree(freqs_single)
    code_single = generate_codes(tree_single)
    encoded_single = encode_text(single_char_text, code_single)
    rebuilt_tree_single = rebuild_tree_from_codes(code_single)
    decoded_single = decode_text(encoded_single, rebuilt_tree_single)
    assert single_char_text == decoded_single, "Test 2 Failed: Single character text mismatch!"
    print(f"Single Character Test ('{single_char_text}'): PASSED\n")

    # Test 3: Empty string edge case
    empty_text = ""
    freqs_empty = build_frequency_table(empty_text)
    tree_empty = build_huffman_tree(freqs_empty)
    code_empty = generate_codes(tree_empty)
    encoded_empty = encode_text(empty_text, code_empty)
    rebuilt_tree_empty = rebuild_tree_from_codes(code_empty)
    decoded_empty = decode_text(encoded_empty, rebuilt_tree_empty)
    assert empty_text == decoded_empty, "Test 3 Failed: Empty text mismatch!"
    print("Empty String Test: PASSED\n")

    print("All backend tests completed successfully!")
