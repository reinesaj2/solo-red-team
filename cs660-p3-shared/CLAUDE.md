# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

- ALWAYS APPLY YOUR DEEPEST AND MOST POWERFUL REASONING ABILITIES

## Project Philosophy

This is CS 660 Project 3: Entity Authentication - designed to develop security mindset through practical password hash analysis. The core philosophy emphasizes:

- **Strategic thinking over brute force**: Identify weakest links before expensive attacks
- **Analysis over automation**: Understanding results is more important than tool output
- **Security mindset development**: Focus on feasibility analysis and resource optimization

## Critical Project Warnings

1. **Weakest Link Principle**: Always identify the most vulnerable authentication method first - avoid attacking computationally expensive hashes when easier targets exist
2. **Resource Management**: If systems are "running really really hot", you're likely on the wrong track
3. **Analysis Required**: Spend minimum 10 minutes carefully reading each hash file before running any tools
4. **No Blind Tool Usage**: Analyze and investigate results rather than copying tool output
5. **Academic Integrity**: JMU Honor Code applies - no online toolkits allowed

## JMU Lab Environment (Critical Rules)

### Infrastructure Constraints
- **stu.cs.jmu.edu**: Gateway only, NOT a lab machine
- **VM Storage**: MUST use `/scratch` directory, NEVER NFS home directory
- **Hardware Requirements**: Not suitable for laptops or VMs on laptops
- **Lab Machines**: 125002-125032, 124802-124832, 1220402-1220435 (.cs.jmu.edu)

### SSH Configuration Templates
- Windows: https://users.cs.jmu.edu/wangxx/Web/Tools/jmucs-ssh-config-win10.txt  
- Mac/Linux: https://users.cs.jmu.edu/wangxx/Web/Tools/jmucs-ssh-config-mac.txt

## Required Prerequisites Knowledge

Students must understand before tool usage:
- Role of one-wayness, salt, and iteration count in password hashing
- LM password hash generation process
- NTLM password hash generation process  
- Linux password hash generation process
- Mathematical notation: v = h^50,000(w||s) where h=hash function, w=password, s=salt, 50,000=iteration count

## Security Tools & Strategic Usage

### Primary Tools
- **Ophcrack**: LM hash cracking with rainbow tables (download separately from https://ophcrack.sourceforge.io/tables.php)
- **John the Ripper**: Multi-format password cracking (see https://www.openwall.com/john/doc/EXAMPLES.shtml)
- **Hydra**: Online password guessing (only if project requires it)
- **Hashcat**: GPU-accelerated cracking (requires hardware GPU support, cannot run on VM)

### Strategic Approach
1. Analyze hash files to identify formats and computational complexity
2. Prioritize attacks by ROI (time/resource vs. success probability)
3. Target weakest authentication links first
4. Use appropriate time limits and resource management

## Specialized Agents

Available security-focused agents for this project:
- **hash-cracking-strategist**: Develops ROI-optimized attack strategies
- **john-ripper-runner**: Controlled John the Ripper execution
- **ophcrack-lm-analyzer**: LM hash rainbow table attacks
- **hydra-brute-force-tester**: Authorized online credential testing
- **hash-file-parser**: Hash file format analysis
- **lab-ssh-configurator**: JMU lab SSH setup
- **evidence-report-assembler**: Technical findings compilation

## Learning Objectives

- Understanding roles of salt and iteration count in mitigating offline dictionary attacks
- Distinguishing between offline dictionary attacks and online password guessing
- Token authentication with private keys (if applicable)
- Ability to quickly locate weakest authentication links in systems

## Project Checklist Management

### Detailed Checklist Reference

The complete project checklist is maintained in **CHECKLIST.md** - a separate file containing all tasks, subtasks, point values, and submission requirements directly extracted from Project3.txt. This checklist serves as both a progress tracker and grading verification tool.

**Key Features of CHECKLIST.md:**
- Uses actual section numbers from Project3.txt (3.7.1, 3.7.2, etc.)
- Includes all point values and submission requirements
- Provides spaces for documenting passwords, tools used, runtimes, and commands
- Maintains separate sections for each task to prevent mixing results
- Includes progress tracking and notes sections

### Checklist Maintenance Protocol

**CRITICAL**: Always maintain both TodoWrite (for active session management) and CHECKLIST.md (for overall project tracking):

#### Session Start Protocol
1. **Review CHECKLIST.md** to understand current project status
2. **Identify next priority tasks** based on weakest link analysis
3. **Load TodoWrite** with 3-5 specific tasks for current session
4. **Mark current task as in_progress** in TodoWrite

#### During Work Protocol
1. **Mark TodoWrite tasks completed** immediately when finished
2. **Update CHECKLIST.md entries** with results as they're discovered:
   - Fill in password fields: `Password: _________` → `Password: matrix123`
   - Document tools used: `Tool: _________` → `Tool: john --format=NT`
   - Record runtimes: `Runtime: _________` → `Runtime: 23 minutes`
   - Check completion boxes: `- [ ]` → `- [x]`
3. **Add command history** to the Command History Log section
4. **Document difficulties** in the Notes section

#### Results Documentation Protocol
When passwords are cracked or analysis is completed:
1. **Update specific CHECKLIST.md entry immediately**
2. **Document exact command used** in Command History Log
3. **Record runtime and any difficulties** in Notes section
4. **Check off completion box** for that specific item
5. **Add follow-up analysis tasks** to TodoWrite if needed

#### Session End Protocol
1. **Update CHECKLIST.md overall progress** (___/75 points)
2. **Document any new challenges discovered** in Notes section
3. **Plan next session priorities** based on unchecked items
4. **Save all progress** - never lose completed work

### CHECKLIST.md Update Examples

**Password Discovery:**
```markdown
- [x] **Morpheus** - Password: matrix123 | Tool: john --format=NT | Runtime: 15 mins
```

**Tool Testing:**
```markdown
- [x] **Install John the Ripper**
  - [x] Review examples at https://www.openwall.com/john/doc/EXAMPLES.shtml  
  - [x] Test basic functionality
```

**Command Documentation:**
```markdown
### Command History Log
john --format=NT --wordlist=/usr/share/wordlists/rockyou.txt win7_hashes.txt
ophcrack-cli -d /tables -t xp_free_small,vista_free win2k3_hashes.txt
hydra -l wangxx -P all8.txt 192.168.100.101 http-post-form "/login.php:username=^USER^&password=^PASS^:Invalid"
```

### Critical Maintenance Rules

1. **Never mark CHECKLIST.md items complete until fully verified**
2. **Always document the exact command that succeeded**
3. **Record both successful and failed attempts for learning**
4. **Separate task results - never mix Windows 7, 2003, and Linux passwords**
5. **Update progress totals regularly to track overall completion**
6. **Use TodoWrite for active session management, CHECKLIST.md for permanent record**

### Coordination Between TodoWrite and CHECKLIST.md

- **TodoWrite**: Active session tasks (3-5 items max)
- **CHECKLIST.md**: Complete project status (75 points total)
- **Sync point**: End of each work session
- **Rule**: TodoWrite completed items must update corresponding CHECKLIST.md entries

## Command Logging Protocol

### COMMANDS.log Maintenance (CRITICAL)

All actions must be logged in **COMMANDS.log** in chronological order:

#### Required Log Entry Format
```
[YYYY-MM-DD HH:MM:SS] [Command/Action] [Purpose] [Result]
```

#### What Must Be Logged
1. **All tool invocations**: john, ophcrack, hydra, hashcat commands
2. **SSH connections**: Connecting to lab machines
3. **File operations**: Reading hash files, creating wordlists
4. **Analysis actions**: Hash format identification, strategic decisions
5. **TodoWrite updates**: Task completions and status changes
6. **CHECKLIST.md updates**: Password discoveries, progress updates

#### Logging Examples
```
[2025-09-08 14:23:15] john --format=NT win7_hashes.txt [Crack Windows 7 NTLM hashes] [Started attack, ETA 45 mins]
[2025-09-08 14:45:32] ophcrack-cli -d /tables win2k3_hashes.txt [Attack LM hashes with rainbow tables] [Cracked 3/5 passwords]
[2025-09-08 15:02:18] TodoWrite: Mark Neo password as completed [Update session progress] [Updated todo status]
[2025-09-08 15:05:41] CHECKLIST.md: Neo password = "redpill" [Document discovered password] [Updated checklist entry]
```

#### Critical Logging Rules
1. **Log BEFORE and AFTER critical commands** (especially long-running attacks)
2. **Always log password discoveries immediately** 
3. **Record failed attempts and reasoning** for learning purposes
4. **Log strategic decisions** (e.g., "Targeting LM hashes first due to rainbow tables")
5. **Never skip logging** - every action must be recorded

#### Integration with Other Files
- **COMMANDS.log**: Complete chronological record of all actions
- **CHECKLIST.md**: Project progress and password results
- **TodoWrite**: Active session task management
- **Sync Rule**: All three must be updated when tasks complete

## Project Structure

This is a security analysis workspace, not a development project:
- No traditional build/test/lint commands
- Students work with provided hash files using system-installed security tools
- Focus on analysis, strategic planning, and results interpretation
- Maintain active checklist with TodoWrite tool throughout entire project
- **Log every action in COMMANDS.log** for complete audit trail


Save all key results as text files in the evidence/ directory.
	•	When running cracking tools (Ophcrack, John, Hashcat, Hydra), redirect the output to a corresponding text file:
	•	evidence/win7_john_results.txt
	•	evidence/win2003_ophcrack_results.txt
	•	evidence/linux_john_results.txt
	•	evidence/html_hydra_results.txt
	•	evidence/basic_hydra_results.txt
	•	evidence/digest_hydra_results.txt
	•	When inspecting certificates/keys, also save outputs:
	•	evidence/rsa_cert.txt
	•	evidence/rsa_private.txt
	•	Continue appending exact commands to COMMANDS.log.
	•	After each run, I’ll take screenshots of the text files with cat to provide clean, readable evidence in the report.