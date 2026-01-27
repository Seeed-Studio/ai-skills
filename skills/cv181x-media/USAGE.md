# CV181X Media Skill - Usage Guide

## Quick Start

### Installation

1. **Install from packaged file**:
```bash
# Package the skill first (if not already packaged)
cd /home/baozhu/storage/reCamera-OS/.claude/skills
python3 skill-creator/scripts/package_skill.py cv181x-media

# The cv181x-media.skill file will be created
```

2. **Use with Claude Code**: The skill will be automatically available when installed in `.claude/skills/` directory

### Basic Usage

The skill automatically triggers when you work with CV181X multimedia tasks. Example triggers:
- "How do I configure VI module to capture 1080p video?"
- "Show me how to add timestamp OSD to video stream"
- "My VENC is dropping frames, how to debug?"
- "How to correct barrel distortion from wide-angle lens?"

## Auto-Update System

### 1. Check for SDK Updates

When a new SDK version is released, check for API changes:

```bash
cd /home/baozhu/storage/reCamera-OS/.claude/skills/cv181x-media

# Update from default SDK path
./scripts/update_from_sdk.sh

# Or specify custom SDK path
./scripts/update_from_sdk.sh /path/to/new/sdk
```

**Output**:
- Lists all API changes (new/removed APIs)
- Saves detailed log to `.update_log_TIMESTAMP.txt`
- Creates temporary directory with extracted API lists

**Next steps after detection**:
1. Review the update log
2. Manually update affected reference/*.md files
3. Test the updated documentation
4. Commit changes with proper version bump

### 2. Learn from Usage Patterns

Collect feedback and analyze usage to improve the skill:

```bash
# Analyze feedback from log file
./scripts/learn_from_usage.py --feedback-file /path/to/usage.log

# Analyze error patterns
./scripts/learn_from_usage.py --analyze-errors /path/to/error.log

# Generate improvement suggestions
./scripts/learn_from_usage.py --suggest-improvements
```

**What it learns**:
- Most frequently queried modules
- Most used APIs
- Common error patterns
- Missing documentation areas

**Output**:
- `.learning_data.json` - Collected usage statistics
- `.suggestions.md` - Actionable improvement suggestions

### 3. Validate Skill Integrity

Before committing changes, validate the skill:

```bash
./scripts/validate_skill.sh
```

**Checks**:
- ✓ All required files present
- ✓ YAML frontmatter correct
- ✓ All reference links valid
- ✓ Module coverage complete
- ✓ Git repository status
- ✓ Scripts executable

## Version Control Workflow

### Making Updates

1. **Create feature branch**:
```bash
git checkout -b feature/add-isp-module
```

2. **Make changes**: Edit SKILL.md or reference files

3. **Validate changes**:
```bash
./scripts/validate_skill.sh
```

4. **Commit changes**:
```bash
git add .
git commit -m "Add ISP module documentation"
```

5. **Merge to main**:
```bash
git checkout main
git merge feature/add-isp-module
```

### Versioning

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (v2.0.0): Breaking changes, major restructuring
- **MINOR** (v1.1.0): New features, new modules added
- **PATCH** (v1.0.1): Bug fixes, typo corrections

**Example workflow**:
```bash
# After adding new module (minor version bump)
git tag -a v1.1.0 -m "Add ISP module documentation"

# After fixing typos (patch version bump)
git tag -a v1.0.1 -m "Fix typos in VENC reference"

# View version history
git tag -l -n1
```

### Update CHANGELOG.md

Always update CHANGELOG.md when making changes:

```markdown
## [1.1.0] - 2026-02-01

### Added
- ISP (Image Signal Processor) module documentation
- 3A algorithm configuration guides

### Changed
- Improved debug.md with more /proc examples

### Fixed
- Typo in VENC rate control example
```

## Continuous Improvement Cycle

```
┌─────────────────────────────────────────────┐
│                                             │
│  1. Usage Monitoring                        │
│     - Collect logs from actual usage        │
│     - Track common queries                  │
│     - Identify pain points                  │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  2. Feedback Analysis                       │
│     - Run learn_from_usage.py               │
│     - Review .suggestions.md                │
│     - Prioritize improvements               │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  3. SDK Monitoring                          │
│     - Check for new SDK releases            │
│     - Run update_from_sdk.sh                │
│     - Review API changes                    │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  4. Update Documentation                    │
│     - Add missing information               │
│     - Improve existing content              │
│     - Add new examples                      │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  5. Validation & Testing                    │
│     - Run validate_skill.sh                 │
│     - Test with real scenarios              │
│     - Verify all links work                 │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  6. Version & Release                       │
│     - Update CHANGELOG.md                   │
│     - Bump version number                   │
│     - Create git tag                        │
│     - Re-package skill                      │
│                                             │
└─────────────────────────────────────────────┘
         │
         └────> Back to Usage Monitoring
```

## Configuration

Edit `.skillrc` to customize behavior:

```bash
# Enable/disable auto-update
AUTO_UPDATE_ENABLED=true

# Set check frequency
CHECK_SDK_UPDATES=monthly
CHECK_USAGE_PATTERNS=weekly

# Enable feedback collection
COLLECT_FEEDBACK=true
```

## Advanced Usage

### Custom SDK Path

If your SDK is in a non-standard location:

```bash
# Edit .skillrc
SDK_PATH=/custom/path/to/sdk
SDK_INCLUDE_PATH=$SDK_PATH/cvi_mpi/include
```

### Remote Repository

Push to remote for team collaboration:

```bash
# Add remote
git remote add origin https://your-git-server/cv181x-media.git

# Push with tags
git push -u origin main --tags
```

### Automated Updates (CI/CD)

Set up automated checks:

```bash
# In cron or CI pipeline
cd /path/to/cv181x-media

# Check for SDK updates weekly
0 0 * * 0 ./scripts/update_from_sdk.sh

# Validate integrity daily
0 2 * * * ./scripts/validate_skill.sh
```

## Troubleshooting

### Update script fails

**Issue**: `update_from_sdk.sh` cannot find headers

**Solution**:
```bash
# Verify SDK path
ls $SDK_PATH/cvi_mpi/include/

# Check .skillrc configuration
cat .skillrc | grep SDK_PATH
```

### Learning script errors

**Issue**: `learn_from_usage.py` fails to parse log

**Solution**:
- Ensure log file exists
- Check log format is compatible
- Run with `--help` to see expected format

### Validation fails

**Issue**: `validate_skill.sh` reports errors

**Solution**:
- Review error messages
- Check for missing files
- Verify YAML frontmatter syntax
- Ensure all reference links are valid

## Best Practices

1. **Commit frequently**: Small, atomic commits are easier to review
2. **Write descriptive messages**: Explain "why" not just "what"
3. **Tag releases**: Use semantic versioning tags
4. **Keep CHANGELOG updated**: Document all user-facing changes
5. **Test before committing**: Always run validate_skill.sh
6. **Review suggestions**: Regularly check `.suggestions.md`
7. **Monitor usage**: Collect and analyze feedback continuously

## Maintenance Schedule

Recommended schedule:

- **Daily**: Monitor for critical issues
- **Weekly**: Review usage patterns, check for quick wins
- **Monthly**: Check SDK updates, minor improvements
- **Quarterly**: Major feature additions, comprehensive review
- **Annually**: Major version release, restructuring if needed

## Support

For issues or questions:
1. Check CHANGELOG.md for recent changes
2. Review .suggestions.md for known issues
3. Check git history: `git log --oneline`
4. Review SDK documentation updates

## Future Enhancements

Planned features:
- [ ] Automated PR creation for SDK updates
- [ ] Interactive web dashboard for usage analytics
- [ ] Integration with CI/CD pipelines
- [ ] Automated testing framework
- [ ] Multi-language support (Chinese documentation)
