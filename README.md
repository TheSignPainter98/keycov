# KeyCov

Kitting is hard.
Making sure that your kitting makes sense requires three things:

1. Coverage of common keyboard types
2. Kits to be offered at a reasonable price and hence do not contain too many units
3. Kitting divisions to make sense to fellow humans

These constraints describe a fundamentally-human task containing a significant arduous part and which hence reduces its affinity with being solved by people.

In response, I wrote this script to give the keycap designer a hand by computing and summarising characteristics of their kitting in response to a set of keyboard layouts to cover.
Hopefully, this should make the task a little less painless, and lead to even better and more creative solutions expressly tailored to each set.

![An example of keycov output](https://raw.githubusercontent.com/TheSignPainter98/keycov/master/img/keycov-example.png)

## Table of Contents


<!-- vim-markdown-toc GFM -->

* [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [Author](#author)

<!-- vim-markdown-toc -->

## Installation

You’ll need a working installation of [python3][python3] and its package manager [pip3][pip3].
Download and unzip the [latest release][latest-release] then open up a terminal and type the following commands.
(These assume that the archive was unzipped in `~/Downloads/keycov/`.)

```bash
cd ~/Downloads/keycov/
pip3 install -r requirements.txt
python3 keycov.py --help
```

A message detailing the usage of `keycov` should now be visible, like the one below.

```
usage: keycov.py [-C] [-c] [-f format] [-h] [-H] [-k dir] [-l dir] [-L num]
                 [-t theme] [-v level]

A little script for helping keycap designers analyse kitting coverage

optional arguments:
  -C, --colour          Force colour output (override default heuristics)
                        (default: False)
  -c, --no-colour       Force no colour output (override default heuristics)
                        (default: False)
...
```

## Usage

Before running, `keycov` will require two things:

1. A folder containing the keyboards the user wishes to support (in [KLE][kle] format).
   By default this the `keebs/` directory next to `keycov.py`.
2. A folder containing the kits the user proposes for their set (in [KLE][kle] format)
   By default this the `kits/` directory next to `keycov.py`.

To run `keycov`, open a terminal and type the following (assuming that the [latest release][latest-release] was unzipped to `~/Downloads/keycov/`.

```bash
cd ~/Downloads/keycov/
python3 keycov.py
```

This will output a basic set of analyses, as it has defaulted to verbosity level 1.
For more information, pass a higher verbosity number by running something like `python3 keycov.py --analysis-verbosity=3`
Details on the analyses performed and the verbosity levels required to output them are shown by passing `keycov` the `--long-help` flag.

## Contributing

If you’d like to contribute, please abide by the [code of conduct.][code-of-conduct]

## Author

This [code][github] was written by Ed Jones (Discord `@kcza#4691`).
I hope floating point errors don’t ruin the nice prime-based set data-structure I used [here.][prime-sets]

[code-of-conduct]: https://github.com/TheSignPainter98/adjust-keys/blob/master/.github/CODE_OF_CONDUCT.md
[github]: http://www.github.com/TheSignPainter98/keycov
[kle]: http://www.keyboard-layout-editor.com "Keyboard layout editor"
[latest-release]: https://github.com/TheSignPainter98/keycov/releases/latest
[pip3]: https://pip.pypa.io/en/stable/
[prime-sets]: https://github.com/TheSignPainter98/keycov/blob/master/src/coverage_analyser.py#L8
[python3]: https://www.python.org
