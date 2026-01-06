#BadHeader
This header has no space after the hash and no blank line after it.

Here is a paragraph with trailing spaces at the end of the line.
And here is another line with too many consecutive blank lines after it.


This is a very very very very very very very very very very very very very very long line that should be wrapped by the linter into multiple lines at the configured width.

## SecondHeader
This header has a space, but still no blank line after it.
```run
#!/bin/bash
# This fenced block is incorrectly tagged with a space before the language
echo "This should be code"
```

``` python
# This fenced code block has a space before the language identifier
print("hello")
```

Normal text before a code block
```bash
echo "this code block should have a blank line before it"
```
Some text immediately after the code block without a blank line.

---

Text without a blank line before this horizontal rule
---
Text without a blank line after this horizontal rule
---

-   [X] Task list item with uppercase X and extra spaces
*   [ ] Another task list item with inconsistent marker and spacing
+   [x] Mixed bullet markers at same level

1.  Numbered list item with extra spaces before the marker
3.  Skipped number that should be renumbered
7.  Another out-of-order item

1. First top-level list
    *Nested bullet with no space after the marker
    + Another nested bullet with inconsistent marker
    3. Nested numbered item starting at 3
        - Deeply nested bullet starting with dash

Paragraph before a list
*No blank line before this list

Paragraph after list
* Another list item without blank line after the previous list

>Quote without space after greater-than
>Another line of the same quote
>Yet another line

>Broken quote without space
Still part of quote but no leading greater-than

Here is a reference-style link definition with bad spacing:
[ref] :https://example.com  "Title"

And here is how it is used: [an example][ref]

This is **bold** text and __also bold__ text and *italic* and _italic_ and ***bold italic*** and __*mixed markers*__ that should be normalized to a consistent style.

Curly quotes: “double quotes” and ‘single quotes’ should be normalized to straight quotes.
Dashes and ellipses: word–word, word—word, and three dots... should be normalized.
Guillemets: «quoted text» should be normalized.

Incorrect emoji names and forms:
:smilie:
:smiley-face:
:heart_eyes_cat:
:octocat:

Inline Attribute Lists (IALs) with bad spacing:

A paragraph with a Kramdown IAL. {:.class #id}

Another paragraph with Pandoc-style IAL.  { .other-class  }

Display math with bad spacing and missing blank lines:
$$
x^2 + y^2 = z^2
$$
Here is some text immediately following math without a blank line.

This $.02 should not be converted to $5 math.

This however $ x^2 $ should be fixed.

```
# None of this should be touched

inline $ math $

$$Display Math$$

3. incorrect list item start
```

| Header 1|Header 2 | Header 3|
|---|:---|---:|
| cell 1|cell 2|cell 3 |
|long cell that should not be wrapped in the table | short | another cell|

A line with Windoending marker ^M
This line simulates CRLF endings and should be normalized.

Trailing whitespace on this line.
Another line with trailing tabs.

Paragraph before list without blank line
7. First
2. Second

Paragraph after code block without blank line
```bash
echo "no blank line before this paragraph"
```
This paragraph should have a blank line before it.

End of file with multiple blank lines following...


