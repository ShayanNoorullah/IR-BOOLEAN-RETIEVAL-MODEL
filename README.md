# IR Boolean Retrieval Model

A Boolean Information Retrieval System with a graphical user interface that supports standard Boolean queries and proximity searches over a collection of document abstracts.

## Features

- **Boolean Query Processing**: Supports AND, OR, NOT operators with proper precedence handling
- **Proximity Search**: Supports queries in the format `term1 term2 /k` where k is the maximum distance between terms
- **Text Preprocessing**: 
  - Tokenization using regular expressions
  - Stopword removal
  - Basic stemming of common English suffixes
- **Index Structures**:
  - Inverted index for basic Boolean retrieval
  - Positional index for proximity queries
- **GUI Interface**:
  - Clean interface built with Tkinter
  - Search history tracking
  - Export inverted index to Excel
  - Real-time query processing

## Setup Instructions

### Prerequisites
- Python 3.6+
- Required Python packages:
  - tkinter (usually comes with Python)
  - pandas
  - json (standard library)
  - re (standard library)
  - os (standard library)

### Installation

1. Clone this repository or download the files
2. Ensure you have the required Python packages installed:
   ```
   pip install pandas
   ```

### Data Preparation
The system expects document abstracts to be in the `Abstracts/` directory as individual text files, with filenames being numeric IDs (e.g., `1.txt`, `2.txt`).

A sample collection of abstracts is included in the repository.

## Usage

1. Run the main application:
   ```
   python Boolean_Model.py
   ```

2. On first run, the system will build the indexes. This may take a moment depending on the number of documents.

3. Enter a query in the search box:
   - For Boolean queries: `information AND retrieval NOT database`
   - For proximity queries: `information retrieval /5`

4. Click "Search" to execute the query
5. View results in the text area
6. Use "History" to view past searches
7. Use "Save Dictionary" to export the inverted index to Excel

## Query Syntax

### Boolean Queries
- Supports AND, OR, NOT operators
- Operators are case-insensitive (both "AND" and "and" work)
- Examples:
  - `information AND retrieval`
  - `information OR data`
  - `information AND (retrieval OR indexing)`
  - `information NOT database`

### Proximity Queries
- Format: `term1 term2 /k`
- Returns documents where term1 and term2 appear within k words of each other
- Example: `information retrieval /5` (finds docs where "information" and "retrieval" are within 5 words of each other)

## Implementation Details

- Text preprocessing includes tokenization, lowercasing, and stopword removal
- Simple stemming removes common suffixes ('ing', 'ed', 'ly', 'es', 's')
- Boolean queries are processed using the Shunting Yard algorithm for operator precedence
- Indexes are persisted as JSON files for reuse between sessions
- GUI is implemented using Tkinter for cross-platform compatibility

## Project Structure

- `Boolean_Model.py`: Main application file with IR implementation and GUI
- `Abstracts/`: Directory containing document abstracts as text files
- `stopwords.txt`: List of stopwords to be filtered out during preprocessing
- `inverted_index.json`: Generated inverted index (term → document IDs)
- `positional_index.json`: Generated positional index (term → document ID → positions)
- `all_docs.json`: List of all document IDs
- `Inverted_Index.xlsx`: Excel export of the inverted index (optional)

## Notes

- The application builds indexes on first run or if index files are missing
- Rebuilding the indexes may be required if documents are added or modified
- For large document collections, initial indexing may take some time 