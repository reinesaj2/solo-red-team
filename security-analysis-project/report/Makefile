# Makefile for CS 660 Project 3 Report
# LaTeX compilation with evidence processing

# Configuration
PDF_NAME=project3_report
MAIN_TEX=main.tex
PYTHON=python3

# Build targets
.PHONY: all report clean clobber check ingest

all: report

# Main build target
report: $(PDF_NAME).pdf

# PDF generation with evidence processing
$(PDF_NAME).pdf: $(MAIN_TEX) ingest
	@echo "Building LaTeX report..."
	latexmk -pdf -interaction=nonstopmode -shell-escape -jobname=$(PDF_NAME) $(MAIN_TEX)
	@echo "Report built successfully: $(PDF_NAME).pdf"

# Evidence ingestion
ingest:
	@echo "Processing evidence files..."
	$(PYTHON) scripts/ingest_evidence.py
	@echo "Evidence processing complete"

# Validation checks
check: report
	@echo "Running validation checks..."
	@echo "1. Checking for inline figures in body sections..."
	@if grep -r "\\includegraphics" sections/ | grep -v "%."; then \
		echo "ERROR: Found inline graphics in body sections!"; \
		exit 1; \
	else \
		echo "✓ No inline graphics in body sections"; \
	fi
	@echo "2. Checking for unresolved references..."
	@if grep -i "??" $(PDF_NAME).log; then \
		echo "WARNING: Found unresolved references"; \
	else \
		echo "✓ All references resolved"; \
	fi
	@echo "3. Checking PDF generation..."
	@if [ -f "$(PDF_NAME).pdf" ]; then \
		echo "✓ PDF generated successfully"; \
		echo "PDF size: $$(du -h $(PDF_NAME).pdf | cut -f1)"; \
	else \
		echo "ERROR: PDF not generated!"; \
		exit 1; \
	fi
	@echo "4. Checking evidence processing..."
	@if [ -f "appendix/figures_autogen.tex" ]; then \
		echo "✓ Evidence figures processed"; \
		echo "Figure count: $$(grep -c '\\begin{figure}' appendix/figures_autogen.tex)"; \
	else \
		echo "ERROR: Evidence not processed!"; \
		exit 1; \
	fi
	@echo "All validation checks passed!"

# Clean temporary files
clean:
	latexmk -c -jobname=$(PDF_NAME)
	rm -f *.aux *.bbl *.blg *.fdb_latexmk *.fls *.log *.out *.toc *.bcf *.run.xml
	rm -f sections/*.aux tables/*.aux appendix/*.aux

# Complete cleanup
clobber: clean
	rm -f $(PDF_NAME).pdf
	rm -f appendix/figures_autogen.tex
	rm -f sections/A0_appendix_index.tex
	rm -f tables/t_traceability.tex
	rm -rf appendix/figures/*
	rm -f traceability.csv

# Quick rebuild
rebuild: clobber all

# Development target with continuous build
watch:
	@echo "Watching for changes..."
	latexmk -pdf -pvc -interaction=nonstopmode -shell-escape -jobname=$(PDF_NAME) $(MAIN_TEX)

# Statistics
stats: report
	@echo "Report Statistics:"
	@echo "=================="
	@echo "PDF size: $$(du -h $(PDF_NAME).pdf | cut -f1)"
	@echo "Page count: $$(pdfinfo $(PDF_NAME).pdf | grep Pages | awk '{print $$2}')"
	@echo "Evidence files: $$(find appendix/figures/ -type f | wc -l)"
	@echo "Figures: $$(grep -c '\\begin{figure}' appendix/figures_autogen.tex)"
	@echo "Tables: $$(find tables/ -name '*.tex' | wc -l)"
	@echo "Word count (approximate): $$(texcount -brief $(MAIN_TEX) sections/*.tex)"

# Help target
help:
	@echo "Available targets:"
	@echo "  all      - Build complete report (default)"
	@echo "  report   - Build PDF report"
	@echo "  ingest   - Process evidence files only"
	@echo "  check    - Run validation checks"
	@echo "  clean    - Remove temporary files"
	@echo "  clobber  - Remove all generated files"
	@echo "  rebuild  - Complete clean rebuild"
	@echo "  watch    - Continuous build on file changes"
	@echo "  stats    - Show report statistics"
	@echo "  help     - Show this help message"