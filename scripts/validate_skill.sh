#!/bin/bash

# validate_skill.sh - Validate skill integrity and completeness

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== CV181X Media Skill Validation ==="
echo "Skill Directory: $SKILL_DIR"
echo ""

ERRORS=0
WARNINGS=0

# Check required files
echo "Step 1: Checking required files..."

required_files=(
    "SKILL.md"
    "references/vi.md"
    "references/vpss.md"
    "references/venc.md"
    "references/vo.md"
    "references/sys.md"
    "references/vb.md"
    "references/rgn.md"
    "references/gdc.md"
    "references/debug.md"
    "references/scenarios.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$SKILL_DIR/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        ((ERRORS++))
    fi
done

echo ""
echo "Step 2: Validating SKILL.md frontmatter..."

# Check YAML frontmatter
if grep -q "^---$" "$SKILL_DIR/SKILL.md"; then
    echo "  ✓ YAML frontmatter found"

    # Check name field
    if grep -q "^name:" "$SKILL_DIR/SKILL.md"; then
        echo "  ✓ 'name' field present"
    else
        echo "  ✗ 'name' field missing"
        ((ERRORS++))
    fi

    # Check description field
    if grep -q "^description:" "$SKILL_DIR/SKILL.md"; then
        echo "  ✓ 'description' field present"

        # Check description length
        desc_length=$(grep "^description:" "$SKILL_DIR/SKILL.md" | wc -c)
        if [ $desc_length -gt 200 ]; then
            echo "  ✓ Description is comprehensive (${desc_length} chars)"
        else
            echo "  ⚠ Description is short (${desc_length} chars)"
            ((WARNINGS++))
        fi
    else
        echo "  ✗ 'description' field missing"
        ((ERRORS++))
    fi
else
    echo "  ✗ YAML frontmatter missing"
    ((ERRORS++))
fi

echo ""
echo "Step 3: Checking reference links..."

# Check if all reference links in SKILL.md exist
ref_links=$(grep -o '\[references/[^]]*\.md\]' "$SKILL_DIR/SKILL.md" | sed 's/\[//;s/\]//' | sort -u)

for link in $ref_links; do
    if [ -f "$SKILL_DIR/$link" ]; then
        echo "  ✓ $link"
    else
        echo "  ✗ $link (BROKEN LINK)"
        ((ERRORS++))
    fi
done

echo ""
echo "Step 4: Validating module coverage..."

# Check if all modules are documented
modules=("VI" "VPSS" "VENC" "VO" "SYS" "VB" "RGN" "GDC")

for module in "${modules[@]}"; do
    if grep -q "${module}" "$SKILL_DIR/SKILL.md"; then
        echo "  ✓ ${module} covered in SKILL.md"
    else
        echo "  ⚠ ${module} not mentioned in SKILL.md"
        ((WARNINGS++))
    fi
done

echo ""
echo "Step 5: Checking git repository..."

if [ -d "$SKILL_DIR/.git" ]; then
    echo "  ✓ Git repository initialized"

    # Check if there are commits
    if git -C "$SKILL_DIR" log -1 &>/dev/null; then
        echo "  ✓ Repository has commits"
        last_commit=$(git -C "$SKILL_DIR" log -1 --format="%h - %s (%cr)")
        echo "    Last commit: $last_commit"
    else
        echo "  ⚠ No commits yet"
        ((WARNINGS++))
    fi
else
    echo "  ⚠ Not a git repository"
    ((WARNINGS++))
fi

echo ""
echo "Step 6: Checking automation scripts..."

scripts=(
    "scripts/update_from_sdk.sh"
    "scripts/learn_from_usage.py"
    "scripts/validate_skill.sh"
)

for script in "${scripts[@]}"; do
    if [ -f "$SKILL_DIR/$script" ]; then
        if [ -x "$SKILL_DIR/$script" ]; then
            echo "  ✓ $script (executable)"
        else
            echo "  ⚠ $script (not executable)"
            ((WARNINGS++))
        fi
    else
        echo "  ✗ $script (MISSING)"
        ((ERRORS++))
    fi
done

echo ""
echo "=== Validation Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo "Status: ✓ PASS (No issues found)"
        exit 0
    else
        echo "Status: ⚠ PASS WITH WARNINGS"
        exit 0
    fi
else
    echo "Status: ✗ FAIL"
    exit 1
fi
