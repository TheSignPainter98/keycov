#!/usr/bin/make

.DEFAULT_GOAL = all

# Build parameters
VERSION = v0.0.1
SEMVERSION = $(subst v,,$(VERSION))

# Sources
KEYCOV_RAW_SRCS = src/keycov.py $(filter-out src/keycov/version.py,$(wildcard src/keycov/*.py))
KEYCOV_RUN_SRCS = src/keycov/version.py $(KEYCOV_RAW_SRCS)
KEYCOV_DATA_SRCS = $(wildcard keebs/*) $(wildcard kits/*) $(wildcard themes/*)
KEYCOV_DIST_SRCS = requirements.txt README.md LICENSE keycov.1.gz ChangeLog $(KEYCOV_RUN_SRCS) $(KEYCOV_DATA_SRCS)
DIST_PKG_SRCS = keycov LICENSE keycov.1.gz ChangeLog
SDIST_PKG_SRCS = LICENSE keycov.1.gz ChangeLog build-binary.sh $(KEYCOV_RUN_SRCS)

# Distributables
AUR_PKGBUILDS = $(foreach p,$(shell ls pkging/aur/),pkging/aur/$p/PKGBUILD)
AUR_DISTS = $(foreach p,$(shell ls pkging/aur/),$p-$(SEMVERSION).tar.xz)
AUR_PKG_THINGS = $(AUR_DISTS) $(AUR_PKGBUILDS)
DISTRIBUTABLES = $(AUR_PKG_THINGS)

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

dist: $(DISTRIBUTABLES)
.PHONY: dist

zip-dist: keycov.zip
.PHONY: dist

build-binary.sh: build-binary.sh.in
	sed 's/KEYCOV_RUN_SRCS/$(subst /,\/,$(KEYCOV_RUN_SRCS))/g'  < $< > $@
	chmod 755 $@

keycov.zip: $(KEYCOV_DIST_SRCS)
	$(ZIP) $@ $^

keycov-$(SEMVERSION).tar.xz: keycov-$(SEMVERSION).tar
	$(XZ) $(XZ_FLAGS) $<

keycov-bin-$(SEMVERSION).tar.xz: keycov-bin-$(SEMVERSION).tar
	$(XZ) $(XZ_FLAGS) $<

keycov-$(SEMVERSION).tar: $(SDIST_PKG_SRCS)
	[[ ! -d $(subst .tar,,$@) ]] && mkdir $(subst .tar,,$@)/ || true
	cp --parents $^ $(subst .tar,,$@)/
	tar -cf $@ $(foreach f,$^,$(subst .tar,,$@)/$f)

keycov-bin-$(SEMVERSION).tar: $(DIST_PKG_SRCS)
	[[ ! -d $(subst .tar,,$@) ]] && mkdir $(subst .tar,,$@)/ || true
	cp --parents $^ $(subst .tar,,$@)/
	tar -cf $@ $(foreach f,$^,$(subst .tar,,$@)/$f)

keycov: $(KEYCOV_RUN_SRCS)
	[[ ! -d keycov-binary/ ]] && mkdir keycov-binary/ || true
	[[ ! -d keycov-binary/ ]] && mkdir keycov-binary/keycov/ || true
	cp --parents $(KEYCOV_RUN_SRCS) keycov-binary/
	cp keycov-binary/src/keycov.py keycov-binary/src/__main__.py
	(cd keycov-binary/src/ && zip -q -MM - $$(find)) > $@-binarytemp
	(echo '#!/usr/bin/env python3' | cat - $@-binarytemp) > $@
	chmod 700 $@

keycov.1.gz: keycov.1
	gzip -kf $<

keycov.1: keycov src/keycov/version.py
	(help2man --no-discard-stderr ./keycov | awk '$$0 == ".SH \"SEE ALSO\"" {exit} 1') < ./$< > $@

src/keycov/version.py: src/keycov/version.py.in keycov.yml
	(sed "s/s_version/$(VERSION)/" | sed "s/s_name/$(shell yq -y .name keycov.yml | head -n1)/" | sed "s/s_desc/$(shell yq -y .desc keycov.yml | head -n1)/") < $< > $@

pkging/aur/keycov-bin/PKGBUILD: pkging/aur/keycov-bin/PKGBUILD.in keycov-bin-$(SEMVERSION).tar.xz keycov.yml scripts/pkggen requirements.txt $(ZIPPED_DIST_PKG)
	./scripts/pkggen $< $@ keycov-bin

pkging/aur/keycov/PKGBUILD: pkging/aur/keycov/PKGBUILD.in keycov-$(SEMVERSION).tar.xz keycov.yml scripts/pkggen requirements.txt $(ZIPPED_DIST_PKG)
	./scripts/pkggen $< $@ keycov

# pkging/aur/%/.SRCINFO: pkging/aur/%/PKGBUILD
	# (cd $(dir $<) && makepkg --printsrcinfo) > $@

keycov.yml: keycov.yml.in
	sed "s/VERSION/$(VERSION)/g" < $< > $@

%.py: ;
%.py.in: ;

requirements.txt: $(KEYCOV_RAW_SRCS)
	pipreqs --force --print >$@

ChangeLog: scripts/change-log.sh scripts/change-log-format.awk $(KEYCOV_RUN_SRCS)
	./$< > $@

clean:
	$(RM) -r requirements.txt src/keycov/version.py keycov.zip __pycache__/ pkging/aur/**/PKGBUILD keycov keycov-*.tar keycov-*.tar.xz keycov.yml $(wildcard *.1) $(wildcard *.1.gz) keycov-binary/ keycov-binarytemp ChangeLog build-binary.sh
