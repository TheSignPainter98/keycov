#!/usr/bin/make

.DEFAULT_GOAL = all

# Build parameters
VERSION = v0.0.1

# Sources
KEYCOV_RAW_SRCS = keycov.py $(wildcard src/*.py)
KEYCOV_RUN_SRCS = src/version.py $(KEYCOV_RAW_SRCS)
KEYCOV_DATA_SRCS = $(wildcard keebs/*) $(wildcard kits/*) $(wildcard themes/*)
KEYCOV_DIST_SRCS = requirements.txt README.md LICENSE $(KEYCOV_RUN_SRCS) $(KEYCOV_DATA_SRCS)

# Programs
ZIP = zip -q -MM

all: $(KEYCOV_RUN_SRCS)
.PHONY: all

run: $(KEYCOV_RUN_SRCS)
	-@python3 ./keycov.py -v3
.PHONY: run

dist: keycov.zip
.PHONY: dist

keycov.zip: $(KEYCOV_DIST_SRCS)
	$(ZIP) $@ $^

src/version.py: src/version.py.in
	sed "s/VERSION/$(VERSION)/g" < src/version.py.in > src/version.py

%.py: ;

requirements.txt: $(KEYCOV_RAW_SRCS)
	pipreqs --force --print >requirements.txt 2>/dev/null

clean:
	$(RM) -r requirements.txt src/version.py keycov.zip __pycache__/
