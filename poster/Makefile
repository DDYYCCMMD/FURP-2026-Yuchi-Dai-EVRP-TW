ROOT := ..
BUILD_DIR := $(ROOT)/tmp/pdfs
MASTER_PDF := $(BUILD_DIR)/poster.pdf
FINAL_PDF := $(ROOT)/FURP_Showcase.pdf

.PHONY: a1 verify

a1:
	mkdir -p $(BUILD_DIR)
	TEXMFCACHE=/tmp/texmf-cache TEXMFVAR=/tmp/texmf-var TEXMFCONFIG=/tmp/texmf-config \
		latexmk -xelatex -interaction=nonstopmode -halt-on-error \
		-outdir=$(BUILD_DIR) poster.tex
	pdfjam --paper a1paper --outfile $(FINAL_PDF) $(MASTER_PDF)

verify:
	pdfinfo $(FINAL_PDF) | grep -E 'Pages|Page size|File size'
