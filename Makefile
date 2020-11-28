#!/usr/bin/make

.DEFAULT_GOAL = all

# Build parameters
VERSION = v0.0.1
RAW_VERSION = $(subst v,,$(VERSION))
DIST_STAMP = keycov-$(RAW_VERSION)
DIST_PKG = $(DIST_STAMP).tar
ZIPPED_DIST_PKG = $(DIST_PKG).xz

# Sources
KEYCOV_RAW_SRCS = src/keycov.py $(filter-out src/keycov/version.py,$(wildcard src/keycov/*.py))
KEYCOV_RUN_SRCS = src/keycov/version.py $(KEYCOV_RAW_SRCS)
KEYCOV_DATA_SRCS = $(wildcard keebs/*) $(wildcard kits/*) $(wildcard themes/*)
KEYCOV_DIST_SRCS = requirements.txt README.md LICENSE keycov.1.gz $(KEYCOV_RUN_SRCS) $(KEYCOV_DATA_SRCS)
DIST_PKG_SRCS = keycov LICENSE keycov.1.gz

# Programs
ZIP = zip -q -MM
XZ = xz
XZ_FLAGS = -kf

all: $(KEYCOV_RUN_SRCS)
.PHONY: all

run: $(KEYCOV_RUN_SRCS)
	-@python3 ./keycov.py -v3
.PHONY: run

github-dist: dist zip-dist
.PHONY: github-dist

dist: $(ZIPPED_DIST_PKG)
.PHONY: dist

zip-dist: keycov.zip
.PHONY: dist

keycov.zip: $(KEYCOV_DIST_SRCS)
	$(ZIP) $@ $^

$(ZIPPED_DIST_PKG): $(DIST_PKG)
	$(XZ) $(XZ_FLAGS) $<

$(DIST_PKG): $(DIST_PKG_SRCS)
	[[ ! -d $(DIST_STAMP) ]] && mkdir $(DIST_STAMP)/ || true
	cp --parents $^ $(DIST_STAMP)/
	tar -cf $@ $(foreach f,$^,$(DIST_STAMP)/$f)

keycov: $(KEYCOV_RUN_SRCS)
	[[ ! -d keycov-bin/ ]] && mkdir keycov-bin/ || true
	[[ ! -d keycov-bin/ ]] && mkdir keycov-bin/keycov/ || true
	cp --parents $(KEYCOV_RUN_SRCS) keycov-bin/
	cp keycov-bin/src/keycov.py keycov-bin/src/__main__.py
	(cd keycov-bin/src/ && zip -q -MM - $$(find)) > $@-bintemp
	(echo '#!/usr/bin/env python3' | cat - $@-bintemp) > $@
	chmod 700 $@

keycov.1.gz: keycov.1
	gzip -kf $<

keycov.1: keycov src/keycov/version.py
	(help2man --no-discard-stderr keycov | awk '$$0 == ".SH \"SEE ALSO\"" {exit} 1') < ./$< > $@

src/keycov/version.py: src/keycov/version.py.in keycov.yml
	(sed "s/s_version/$(VERSION)/" | sed "s/s_name/$(shell yq -y .name keycov.yml | head -n1)/" | sed "s/s_desc/$(shell yq -y .desc keycov.yml | head -n1)/") < $< > $@

pkging/aur/%/PKGBUILD: pkging/aur/%/PKGBUILD.in scripts/pkggen keycov.yml requirements.txt $(ZIPPED_DIST_PKG)
	./scripts/pkggen $< $@

keycov.yml: keycov.yml.in
	sed "s/VERSION/$(VERSION)/g" < $< > $@

%.py: ;
%.py.in: ;

requirements.txt: $(KEYCOV_RAW_SRCS)
	pipreqs --force --print >$@

clean:
	$(RM) -r requirements.txt src/keycov/version.py keycov.zip __pycache__/ pkging/PKGBUILD keycov keycov-*.tar keycov-*.tar.xz keycov.yml $(wildcard *.1) $(wildcard *.1.gz) keycov-bin/ keycov-bintemp $(DIST_STAMP)/
