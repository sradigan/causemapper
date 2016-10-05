# causemapper

This project aims to create graphical maps from text based input for the **cause mapping** technique used for **Root Cause Analysis** developed by [ThinkReliability](http://www.thinkreliability.com/).

## Requirements
 * python3
 * [graphviz](http://www.graphviz.org/)

## Usage
```
./genmap.py -f path/to/input/file.json | dot -Tps -o outfile.pdf
```
```
./genmap.py -f path/to/input/file.json -o output.gv
dot -Tps output.gv -o outfile.pdf
```

## Why?
Drawing is tedious.

## Where are the orthogonal lines?
Graphviz has not yet implemented support for "ports" with ortho splines, which is what is used to draw a line directly to the "content" block in the drawing.

## Contributing
If you would like to contribute to this project, please fork it and make a pull request.

## Example
Simple:

![sample_outline](https://raw.githubusercontent.com/sradigan/causemapper/master/examples/sample_outline.png "sample_outline")
