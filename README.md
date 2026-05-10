# CSE 4802 — Lexical Analyzer
### Compiler Design Lab | Section 1B | Assignment 1

---

## 📌 About

A hand-written **lexical analyzer** (no Lex/Flex) for a C-like language, built as part of CSE 4802 Compiler Design Lab. It reads source code, classifies every token, builds a symbol table, and reports statistics — all from scratch using regular expressions and a manual scanning loop.

Also includes a **standalone browser-based visual tool** (`lexer_tool.html`) to analyze code interactively without running any terminal commands.

---

## 📁 Project Structure

```
CSE4802-Lexical-Analyzer/
│
├── lexer.py              # Core Python lexical analyzer
├── lexer_tool.html       # Interactive browser tool (no install needed)
├── your_code.c           # Sample input file
└── README.md             # This file
```

---

## ⚙️ How It Works

The lexer scans source code character by character, applying the following rules in order:

1. **String & character literals** — matched first to avoid conflicts
2. **Multi-character operators** — `>=`, `<=`, `==`, `!=`, `&&`, `||`, `++`, `--`, `<<`, `>>`, `+=`, etc.
3. **Single-character operators** — `+`, `-`, `*`, `/`, `=`, `<`, `>`, etc.
4. **Delimiters** — `( ) { } [ ] ; , .`
5. **Invalid identifiers** — e.g. `9abc` (caught as errors)
6. **Float constants** — e.g. `3.14`, `2.5e-3`
7. **Integer constants** — e.g. `10`, `0`, `255`
8. **Keywords & Identifiers** — keywords take priority

> **Longest Match Rule** is always enforced: `>=` is matched before `>` and `=` separately. `++` is matched before two separate `+` tokens.

---

## 🪙 Token Categories

| Category | Examples |
|---|---|
| `KEYWORD` | `int`, `float`, `if`, `while`, `return` |
| `IDENTIFIER` | `a`, `sum`, `result`, `myVar` |
| `INTEGER_CONST` | `10`, `0`, `255` |
| `FLOAT_CONST` | `3.14`, `2.5e-3` |
| `CHAR_CONST` | `'x'`, `'\n'` |
| `STRING_CONST` | `"hello"`, `"world"` |
| `ARITHMETIC_OP` | `+`, `-`, `*`, `/`, `%` |
| `RELATIONAL_OP` | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| `LOGICAL_OP` | `&&`, `\|\|`, `!` |
| `BITWISE_OP` | `&`, `\|`, `^`, `~`, `<<`, `>>` |
| `ASSIGNMENT_OP` | `=`, `+=`, `-=`, `*=`, `/=`, `<<=`, `>>=` |
| `INCR_DECR_OP` | `++`, `--` |
| `DELIMITER` | `(`, `)`, `{`, `}`, `[`, `]`, `;`, `,` |

---

## 🚀 How to Run

### Requirements
- Python 3.x
- No external libraries needed

### Step 1 — Create your input file

Create a file called `your_code.c` and write any C-like code inside it:

```c
int a = 10;
float b = 3.14;
if (a >= b && b != 0) {
    a++;
}
int sum = a + b;
char c = 'x';
```

### Step 2 — Run the lexer

```bash
python3 lexer.py your_code.c
```

### Step 3 — Read the output

The terminal will print:

- **Token Stream** — every token with its type and line number
- **Token Statistics** — counts for every category
- **Symbol Table** — identifiers with frequency and first occurrence line
- **Lexical Errors** — any invalid tokens found

---

## 🖥️ Interactive Visual Tool

Open `lexer_tool.html` in any browser — no installation, no internet required.

**Features:**
- Paste any C-like code and click **Analyze**
- Switch between **Token Stream**, **Statistics**, and **Symbol Table** tabs
- Errors appear highlighted in red automatically
- Works unlimited times, fully offline

**To use inside VS Code:**
1. Install the **Live Preview** extension by Microsoft
2. Open `lexer_tool.html`
3. Click **Show Preview** (browser icon, top right)

---

## 📤 Sample Output

**Input:**
```c
int a = 10;
float b = 3.14;
if (a >= b && b != 0) {
    a++;
}
```

**Token Stream (excerpt):**
```
<KEYWORD, int>          [line 1]
<IDENTIFIER, a>         [line 1]
<ASSIGNMENT_OP, =>      [line 1]
<INTEGER_CONST, 10>     [line 1]
<DELIMITER, ;>          [line 1]
<KEYWORD, float>        [line 2]
<IDENTIFIER, b>         [line 2]
<ASSIGNMENT_OP, =>      [line 2]
<FLOAT_CONST, 3.14>     [line 2]
...
```

**Statistics:**
```
Total Tokens          : 73
Keywords              : 9
Identifiers           : 23
Constants             : 5
  Integer Constants   : 3
  Float Constants     : 1
  Character Constants : 1
Operators             : 19
Delimiters            : 17
```

**Symbol Table:**
```
Identifier      Count   First Line
──────────────────────────────────
a                   9            1
b                   8            2
result              1           11
sum                 1            6
```

---

## 🔒 Constraints

- ❌ Does **not** use Lex, Flex, Yacc, or Bison
- ✅ Manual character-by-character scanning
- ✅ Standard Python `re` module only
- ✅ Implementation language: **Python 3**

---

## 📚 Course Info

| Field | Detail |
|---|---|
| Course | CSE 4802 — Compiler Design Lab |
| Section | 1AB |
| Assignment | 1 — Lexical Analyzer |
| Language | Python 3 |
| Topic | Lexical Analysis, Token Classification, Symbol Table |
