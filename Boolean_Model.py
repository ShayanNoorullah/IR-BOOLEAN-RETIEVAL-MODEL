# THIS ASSIGNMENT HAS BEEN MADE BY SHAYAN 22K-4148 FROM BCS-6H
import os
import re
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
from collections import defaultdict
import pandas as pd

# THE FUNCTION 'load_stopwords' LOADS STOPWORDS FROM THE ALREADY PROVIDED FILE i.e. 'stopwords.txt':
def load_stopwords(filename="stopwords.txt"):
    #Load stopwords from a text file into a set
    with open(filename, "r") as f:
        return set(f.read().splitlines())

# STOPWORDS IS A SET STORING THE STOPWORDS LOADED FROM 'stopwords.txt' FILE:
STOPWORDS = load_stopwords()

# THE PREPROCESSING IS DONE BY THE 'preprocess' FUNCTION WHICH INCLUDES TOKENISATION using REGEX, LOWERCASING AND REMOVAL OF STOPWORDS SEQUENTIALLY:
def preprocess(text):
    tokens = re.findall(r'\b\w+\b', text.lower())
    return [word for word in tokens if word not in STOPWORDS]

# THE SIMPLE STEM FUNCTION IS USED TO PERFORM SIMPLE SUFFIX STEMMING CONSIDERING COMMON ENGLISH WORD ENDINGS:
def simple_stem(word):
    suffixes = ['ing', 'ed', 'ly', 'es', 's']
    for suffix in suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

# THE 'build_indexes' FUNCTION BUILD INVERTED AND POSITIONAL INDEXES FOR THE DOCUMENTS:
def build_indexes(directory):
    inverted_index = defaultdict(set)
    positional_index = defaultdict(lambda: defaultdict(list))
    all_docs = set()

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            doc_id = int(filename.split(".")[0])
            all_docs.add(doc_id)
            with open(os.path.join(directory, filename), "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            tokens = preprocess(text)
            for position, token in enumerate(tokens):
                stemmed_word = simple_stem(token)
                inverted_index[stemmed_word].add(doc_id)
                positional_index[stemmed_word][doc_id].append(position)
    return inverted_index, positional_index, all_docs

# THE 'save_indexes' FUNCTION SERIALIZES INDEXES INTO JSON FILES WHICH ARE STORED IN THE SAME FOLDER:
def save_indexes(inverted_index, positional_index, all_docs):
    with open("inverted_index.json", "w") as f:
        json.dump({k: list(v) for k, v in inverted_index.items()}, f)
    with open("positional_index.json", "w") as f:
        json.dump({k: {doc: pos for doc, pos in v.items()} for k, v in positional_index.items()}, f)
    with open("all_docs.json", "w") as f:
        json.dump(list(all_docs), f)

# THE 'load_indexes' FUNCTION LOADS PREBUILT INDEXES FROM JSON FILES BUILD BY 'save_indexs' FUNCTION:
def load_indexes():
    with open("inverted_index.json", "r") as f:
        inverted_index = json.load(f)
    with open("positional_index.json", "r") as f:
        positional_index = json.load(f)
    with open("all_docs.json", "r") as f:
        all_docs = set(json.load(f))
    return inverted_index, positional_index, all_docs

# THE 'proess_boolean_query' FUNTION PROCESSES THE INPUTTED BOOLEAN QUERY BASED ON ALREADY SET OPERATOR PRECEDENCE WHICH HANDLES MULTI OPERATOR QUERIES UPTO 3 TERMS::
def process_boolean_query(query, inverted_index, all_docs):
    # POSTFIX NOTATION CONVERSION USING SHUNTING YARD ALGORITHM
    precedence = {'not': 3, 'and': 2, 'or': 1}
    output = []
    operator_stack = []
    
    # TOKENIZING QUERY WHILE HANDLING MULTI TERMS
    tokens = re.findall(r'\"(.+?)\"|(\b(?:and|or|not)\b)|\b(\w+)\b', query.lower())
    cleaned_tokens = [t[0] or t[1] or t[2] for t in tokens if any(t)]

    for token in cleaned_tokens:
        if token in ['and', 'or', 'not']:
            while (operator_stack and 
                   operator_stack[-1] != '(' and 
                   precedence[operator_stack[-1]] >= precedence[token]):
                output.append(operator_stack.pop())
            operator_stack.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            operator_stack.pop()
        else:
            output.append(token)

    while operator_stack:
        output.append(operator_stack.pop())

    # EVALUATION POSTFIX NOTATIONS
    stack = []
    all_docs = set(map(int, all_docs))
    for token in output:
        if token == 'not':
            operand = stack.pop()
            stack.append(all_docs - operand)
        elif token == 'and':
            right = stack.pop()
            left = stack.pop()
            stack.append(left & right)
        elif token == 'or':
            right = stack.pop()
            left = stack.pop()
            stack.append(left | right)
        else:
            term = simple_stem(token)
            stack.append(set(map(int, inverted_index.get(term, []))))
    return sorted(stack.pop()) if stack else []

# THE 'process_proximity_query' FUNCTION HANDLES PROXIMITY QUERIES IN THE FORMAT 'term1 term2 /k' SPECIFIED IN THE ASSIGNMENT:
def process_proximity_query(query, positional_index):
    parts = query.lower().split("/")
    terms = parts[0].split()
    k = int(parts[1])
    term1, term2 = simple_stem(terms[0]), simple_stem(terms[1])
    common_docs = set(positional_index.get(term1, {}).keys()) & set(positional_index.get(term2, {}).keys())
    results = []
    for doc in common_docs:
        positions1 = positional_index[term1][doc]
        positions2 = positional_index[term2][doc]
        for p1 in positions1:
            if any(abs(p1 - p2) <= k for p2 in positions2):
                results.append(int(doc))
                break
    return sorted(results)

# GUI APPLICATION IMPLEMENTATION USING TKINTER LIBRARY:
class SearchApplication:
    def __init__(self, root):
        self.search_history = []
        self.inverted_index, self.positional_index, self.all_docs = self.initialize_indexes()
        
        # SETTING UP THE GUI:
        root.title("IR Boolean Retrieval Model")
        root.geometry("700x550")
        root.configure(bg="#f0f0f0")

        frame = tk.Frame(root, bg="#f0f0f0")
        frame.pack(expand=True, fill='both', padx=20, pady=20)

        # FOR INPUTTING QUERY:
        tk.Label(frame, text="Enter Query:", bg="#f0f0f0", font=("Arial", 12)).pack(anchor='w')
        self.query_entry = tk.Entry(frame, width=60, font=("Arial", 12))
        self.query_entry.pack(pady=5, fill='x')

        # FOR BUTTONS:
        button_frame = tk.Frame(frame, bg="#f0f0f0")
        button_frame.pack(pady=10, fill='x')
        
        buttons = [
            ("Search", "#4CAF50", self.search),
            ("Save Dictionary", "#FF9800", self.save_dictionary),
            ("History", "#2196F3", self.show_history),
            ("Exit", "#F44336", root.destroy)
        ]
        
        for text, color, command in buttons:
            tk.Button(button_frame, text=text, bg=color, fg="white", 
                     font=("Arial", 10, "bold"), command=command).pack(side='left', padx=5)

        # FOR DISPLAYING THE RESULT:
        self.result_text = scrolledtext.ScrolledText(frame, width=80, height=15, 
        font=("Consolas", 10), state=tk.DISABLED)
        self.result_text.pack(pady=10, fill='both', expand=True)

    # LOADING AND REBUILDING OF INDEXES IF THE PROGRAM IS STARTING FOR FIRST TIME AND INDEXES ARE NOT FORMED PREVIOUSLY:
    def initialize_indexes(self):
        try:
            return load_indexes()
        except FileNotFoundError:
            messagebox.showinfo("Info", "Building indexes... This may take a moment.")
            inv_idx, pos_idx, all_d = build_indexes("Abstracts")
            save_indexes(inv_idx, pos_idx, all_d)
            return inv_idx, pos_idx, all_d

    # handling SEARCH OPERATIONS WITH PROMPTING IF NO QUERY IS ENTERED: 
    def search(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return
        try:
            if "/" in query:
                result = process_proximity_query(query, self.positional_index)
            else:
                result = process_boolean_query(query, self.inverted_index, self.all_docs)
            self.search_history.append((query, result))
            self.display_results(result)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid query format: {str(e)}")

    # FOR DISPLAYING THE RESULTS OF SEARCH QUERY:
    def display_results(self, result):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        if result:
            output = f"Found {len(result)} documents:\n" + ", ".join(map(str, result))
        else:
            output = "No matching documents found"
        self.result_text.insert(tk.END, output)
        self.result_text.config(state=tk.DISABLED)

    # FOR DISPLAYING THE HISTORY OF SEARCH QUERIES SO FAR:
    def show_history(self):
        history = "\n\n".join([f"Query: {q}\nResults: {', '.join(map(str, r)) if r else 'None'}" 
                            for q, r in self.search_history])
        messagebox.showinfo("Search History", history or "No history available")
    
    # FOR SAVING THE INVERTED INDEX TO AN EXCEL FILE:
    def save_dictionary(self):
        data = {"Term": [], "Documents": []}
        for term, docs in self.inverted_index.items():
            data["Term"].append(term)
            data["Documents"].append(", ".join(map(str, sorted(docs))))
        
        pd.DataFrame(data).to_excel("Inverted_Index.xlsx", index=False)
        messagebox.showinfo("Success", "Inverted index exported to Inverted_Index.xlsx")

# THE MAIN FUNCTION THAT RUNS THE GUI AND THE BOOLEAN RETRIEVAL MODEL IMPLEMENTATION
if __name__ == "__main__":
    root = tk.Tk()
    app = SearchApplication(root)
    root.mainloop()