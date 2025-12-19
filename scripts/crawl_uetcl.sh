#!/bin/bash
# UETCL Document Crawler & Ingestion Script
# Downloads PDFs from uetcl.go.ug and ingests them into SISUiQ

set -e

DOCS_DIR="/Users/masinde/pytorch-test/LLMS/UETCL/data/uetcl"
mkdir -p "$DOCS_DIR"

echo "📥 Downloading UETCL Documents..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Direct PDF downloads from uetcl.go.ug
declare -A DOCUMENTS=(
    ["UETCL-Annual-Report-2022-2023.pdf"]="https://uetcl.go.ug/wp-content/uploads/2024/04/UETCL-Annual-Report-2022-2023_compressed.pdf"
    ["UETCL-Annual-Report-2021-2022.pdf"]="https://uetcl.go.ug/wp-content/uploads/2024/04/Annual-Report-2021-2022-compressed-1.pdf"
    ["UETCL-Annual-Report-2019-2020.pdf"]="https://uetcl.go.ug/wp-content/uploads/2024/04/Annual-Report-2019-2020s_compressed.pdf"
    ["UETCL-Grid-Development-Plan-2018-2040.pdf"]="https://uetcl.go.ug/wp-content/uploads/2024/04/Grid-Development-Plan-2018-2040.pdf"
    ["UETCL-Corporate-Business-Plan-2019-2024.pdf"]="https://uetcl.go.ug/wp-content/uploads/2024/04/UETCL-Corporate-Business-Plan-2019-2024.pdf"