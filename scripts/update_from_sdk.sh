#!/bin/bash

# update_from_sdk.sh - Auto-update skill from new SDK release
# Usage: ./update_from_sdk.sh <SDK_PATH>

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SDK_PATH="${1:-/home/baozhu/storage/reCamera-OS/output/sg2002_recamera_emmc}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
UPDATE_LOG="$SKILL_DIR/.update_log_$TIMESTAMP.txt"

echo "=== CV181X Media Skill Auto-Update ===" | tee "$UPDATE_LOG"
echo "SDK Path: $SDK_PATH" | tee -a "$UPDATE_LOG"
echo "Skill Dir: $SKILL_DIR" | tee -a "$UPDATE_LOG"
echo "" | tee -a "$UPDATE_LOG"

# Check if SDK path exists
if [ ! -d "$SDK_PATH" ]; then
    echo "ERROR: SDK path does not exist: $SDK_PATH" | tee -a "$UPDATE_LOG"
    exit 1
fi

# Function to extract API list from header
extract_apis() {
    local module=$1
    local header=$2
    local output=$3

    echo "Extracting APIs from $module..." | tee -a "$UPDATE_LOG"

    if [ -f "$SDK_PATH/cvi_mpi/include/$header" ]; then
        grep "^CVI_S32 CVI_${module}_" "$SDK_PATH/cvi_mpi/include/$header" | \
            sed 's/(.*//g' | sort > "$output"
        local count=$(wc -l < "$output")
        echo "  Found $count APIs in $module" | tee -a "$UPDATE_LOG"
    else
        echo "  WARNING: Header not found: $header" | tee -a "$UPDATE_LOG"
    fi
}

# Create temporary directory for extracted data
TMP_DIR="$SKILL_DIR/.tmp_update_$TIMESTAMP"
mkdir -p "$TMP_DIR"

echo "Step 1: Extracting API lists from SDK headers..." | tee -a "$UPDATE_LOG"

extract_apis "VI" "cvi_vi.h" "$TMP_DIR/vi_apis.txt"
extract_apis "VPSS" "cvi_vpss.h" "$TMP_DIR/vpss_apis.txt"
extract_apis "VENC" "cvi_venc.h" "$TMP_DIR/venc_apis.txt"
extract_apis "VO" "cvi_vo.h" "$TMP_DIR/vo_apis.txt"
extract_apis "VB" "cvi_vb.h" "$TMP_DIR/vb_apis.txt"
extract_apis "RGN" "cvi_region.h" "$TMP_DIR/rgn_apis.txt"
extract_apis "GDC" "cvi_gdc.h" "$TMP_DIR/gdc_apis.txt"

echo "" | tee -a "$UPDATE_LOG"
echo "Step 2: Detecting API changes..." | tee -a "$UPDATE_LOG"

# Function to detect changes
detect_changes() {
    local module=$1
    local new_apis="$TMP_DIR/${module,,}_apis.txt"
    local ref_doc="$SKILL_DIR/references/${module,,}.md"

    if [ ! -f "$new_apis" ]; then
        return
    fi

    echo "Checking $module for changes..." | tee -a "$UPDATE_LOG"

    # Extract current APIs from reference doc
    if [ -f "$ref_doc" ]; then
        grep "^- \`CVI_${module}_" "$ref_doc" | sed 's/^- `//;s/()`.*//g' | sort > "$TMP_DIR/${module,,}_current.txt" 2>/dev/null || touch "$TMP_DIR/${module,,}_current.txt"

        # Find new APIs
        local new_count=$(comm -13 "$TMP_DIR/${module,,}_current.txt" "$new_apis" | wc -l)

        # Find removed APIs
        local removed_count=$(comm -23 "$TMP_DIR/${module,,}_current.txt" "$new_apis" | wc -l)

        if [ $new_count -gt 0 ] || [ $removed_count -gt 0 ]; then
            echo "  ⚠️  Changes detected:" | tee -a "$UPDATE_LOG"
            [ $new_count -gt 0 ] && echo "    + $new_count new APIs" | tee -a "$UPDATE_LOG"
            [ $removed_count -gt 0 ] && echo "    - $removed_count removed APIs" | tee -a "$UPDATE_LOG"

            # Save detailed changes
            if [ $new_count -gt 0 ]; then
                echo "    New APIs:" | tee -a "$UPDATE_LOG"
                comm -13 "$TMP_DIR/${module,,}_current.txt" "$new_apis" | sed 's/^/      /g' | tee -a "$UPDATE_LOG"
            fi
            if [ $removed_count -gt 0 ]; then
                echo "    Removed APIs:" | tee -a "$UPDATE_LOG"
                comm -23 "$TMP_DIR/${module,,}_current.txt" "$new_apis" | sed 's/^/      /g' | tee -a "$UPDATE_LOG"
            fi
        else
            echo "  ✓ No changes" | tee -a "$UPDATE_LOG"
        fi
    else
        echo "  WARNING: Reference doc not found: $ref_doc" | tee -a "$UPDATE_LOG"
    fi
}

detect_changes "VI"
detect_changes "VPSS"
detect_changes "VENC"
detect_changes "VO"
detect_changes "VB"
detect_changes "RGN"
detect_changes "GDC"

echo "" | tee -a "$UPDATE_LOG"
echo "Step 3: Checking SDK version..." | tee -a "$UPDATE_LOG"

if [ -f "$SDK_PATH/install/soc_sg2002_recamera_emmc/tpu_musl_riscv64/cvitek_tpu_sdk/include/cviruntime.h" ]; then
    SDK_VERSION=$(grep -E "#define.*VERSION" "$SDK_PATH/install/soc_sg2002_recamera_emmc/tpu_musl_riscv64/cvitek_tpu_sdk/include/cviruntime.h" | head -1 || echo "Unknown")
    echo "SDK Version: $SDK_VERSION" | tee -a "$UPDATE_LOG"
fi

echo "" | tee -a "$UPDATE_LOG"
echo "Step 4: Update summary" | tee -a "$UPDATE_LOG"
echo "  - Extracted API lists saved to: $TMP_DIR" | tee -a "$UPDATE_LOG"
echo "  - Update log saved to: $UPDATE_LOG" | tee -a "$UPDATE_LOG"
echo "  - Review changes and update reference docs manually" | tee -a "$UPDATE_LOG"
echo "" | tee -a "$UPDATE_LOG"
echo "Step 5: Next actions" | tee -a "$UPDATE_LOG"
echo "  1. Review $UPDATE_LOG for API changes" | tee -a "$UPDATE_LOG"
echo "  2. Update affected reference/*.md files" | tee -a "$UPDATE_LOG"
echo "  3. Test updated skill" | tee -a "$UPDATE_LOG"
echo "  4. Commit changes: git add . && git commit -m 'Update from SDK vX.Y.Z'" | tee -a "$UPDATE_LOG"
echo "  5. Tag version: git tag v1.1.0" | tee -a "$UPDATE_LOG"
echo "  6. Re-package: python3 ../../skill-creator/scripts/package_skill.py ." | tee -a "$UPDATE_LOG"

echo "" | tee -a "$UPDATE_LOG"
echo "=== Update check completed ===" | tee -a "$UPDATE_LOG"

# Keep temp directory for manual review
echo ""
echo "Temporary files kept in: $TMP_DIR"
echo "Update log: $UPDATE_LOG"
