# KeyCov

Designing good, original kitting is a surprisingly difficult problem.
In particular, we require that:

1. Common keyboards are covered
2. Individual kits are reasonably small so they may be offered relatively cheaply
3. A particular customer should not be expected to require too many kits
4. The overall number of kits is not absurdly high
5. The assignment of keys into kits makes sense to fellow humans.

What we have, therefore, is a fundamentally-human problem which contains parts which require a large amount of repetitive work.

Therefore, I wrote this script to give the keycap designer a hand by analysing their kitting choices in response to a set of keyboard layouts to cover.
These characteristics should help give an idea of how kitting will be perceived and used by (rational) potential customers.

Hopefully this should give the designer some peace-of-mind in their existing decisions and hence the path to novel and creative kitting solutions, well-tailored to their set should be somewhat easier.

![An example of keycov output](https://raw.githubusercontent.com/TheSignPainter98/keycov/master/img/keycov-example.png)

## Table of Contents


<!-- vim-markdown-toc GFM -->

* [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [Author and Random Notes](#author-and-random-notes)

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

A message detailing the usage of KeyCov should now be visible, like the one below.

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

Before running, KeyCov will require two things:

1. A folder containing the keyboards the user wishes to support (in [KLE][kle] format).
   By default this the `keebs/` directory next to `keycov.py`.
2. A folder containing the kits the user proposes for their set (in [KLE][kle] format)
   By default this the `kits/` directory next to `keycov.py`.

To run KeyCov, open a terminal and type the following (assuming that the [latest release][latest-release] was unzipped to `~/Downloads/keycov/`).

```bash
cd ~/Downloads/keycov/
python3 keycov.py
```

This will output a basic set of analyses; KeyCov defaults to verbosity level 1.
For more information, pass a higher verbosity number by running something like `python3 keycov.py --analysis-verbosity=3`
Details on the analyses performed and the verbosity levels required to output them are shown by passing KeyCov the `--long-help` flag.

Aside from text, KeyCov supports `json` and `yaml` output formats to allow an interface with a more customer-friendly front-end (e.g a keycap set website).

## Contributing

Contributions are welcome!
If you’d like to contribute, please abide by the [code of conduct.][code-of-conduct]

## Author and Random Notes

This [code][github] was written by Ed Jones (Discord `@kcza#4691`).

I hope floating point errors don’t ruin the nice prime-based set data-structure I used [here.][prime-sets]

Please don’t be surprised if KeyCov takes a while to perform its analyses, finding a minimum-size set of kits which cover a keyboard is believed to be a computationally-hard problem (the time to solve it scales very poorly with the size of the input).
More specifically, it reduces to [set cover,][set-cover] a standard problem in theoretical computer science for which:

1. We do not know of an algorithm which runs in less-than exponential time and,
2. We do not know whether one _can_ or _cannot_ exist on our classical hardware.

[code-of-conduct]: https://github.com/TheSignPainter98/adjust-keys/blob/master/.github/CODE_OF_CONDUCT.md
[github]: http://www.github.com/TheSignPainter98/keycov
[kle]: http://www.keyboard-layout-editor.com "Keyboard layout editor"
[latest-release]: https://github.com/TheSignPainter98/keycov/releases/latest
[pip3]: https://pip.pypa.io/en/stable/
[prime-sets]: https://github.com/TheSignPainter98/keycov/blob/master/src/coverage_analyser.py#L8
[python3]: https://www.python.org
[set-cover]: https://www.geeksforgeeks.org/set-cover-problem-set-1-greedy-approximate-algorithm/
