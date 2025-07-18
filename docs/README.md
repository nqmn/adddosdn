# 📚 AdDDoSDN Documentation Hub

Welcome to the comprehensive documentation for the AdDDoSDN Dataset Generation Framework! This directory contains everything you need to understand, install, and use the framework effectively.

## 🚀 Quick Navigation

### 🎯 **New Users - Start Here!**
1. **[📖 Project Summary](summary.md)** - High-level overview of what this framework does
2. **[⚙️ Installation Guide](install.md)** - Step-by-step setup instructions
3. **[🎭 Attack Scenarios](scenario.md)** - Understanding the network setup and attacks

### 🔬 **Researchers & Developers**
4. **[📊 Dataset Analysis](analysis.md)** - Detailed feature descriptions and statistics
5. **[📈 Development Progress](progress.md)** - Recent updates and changelog

## 📂 Documentation Structure

```
📂 docs/
├── 📄 README.md           ← This file - Your starting point
├── 📖 summary.md          ← Project overview for beginners
├── ⚙️ install.md          ← Complete installation guide
├── 🎭 scenario.md         ← Network setup and attack details
├── 📊 analysis.md         ← Dataset features and statistics
└── 📈 progress.md         ← Development history and updates
```

## 🎯 Quick Start Paths

### Path 1: "I'm new to cybersecurity datasets"
```
summary.md → install.md → scenario.md
```
Start with the big picture, learn how to set it up, then understand what attacks it generates.

### Path 2: "I need datasets for my research"
```
analysis.md → scenario.md → install.md
```
Jump to the technical details about features and data, understand the scenarios, then set it up.

### Path 3: "I want to contribute or modify the code"
```
progress.md → analysis.md → scenario.md
```
See what's been done recently, understand the technical architecture, then dive into scenarios.

## 🔍 What You'll Find

### 📖 Project Summary
- **What:** High-level explanation of the framework's purpose
- **Why:** Benefits for cybersecurity research and education
- **Who:** Target users and use cases
- **When:** Best situations to use this framework

### ⚙️ Installation Guide
- **System Requirements:** Hardware and software needs
- **Step-by-Step Setup:** From zero to running dataset generation
- **Troubleshooting:** Common issues and solutions
- **Verification:** How to confirm everything works

### 🎭 Attack Scenarios
- **Network Architecture:** How the virtual network is structured
- **Attack Types:** Detailed descriptions of all implemented attacks
- **Timeline:** When each attack happens during generation
- **Host Roles:** What each virtual computer does

### 📊 Dataset Analysis
- **Three Synchronized Formats:** Complete descriptions of packet-level (15 features), SDN flow (18 features), and CICFlow aggregated (85 features) data
- **Data Formats:** What the output files contain and their relationships
- **Statistics:** Expected data distributions and characteristics across all formats
- **Quality Metrics:** How to validate your generated datasets and timeline integrity

### 📈 Development Progress
- **Recent Updates:** Latest improvements and bug fixes
- **Version History:** Major milestones and changes
- **Current Status:** What works and what's in development
- **Future Plans:** Upcoming features and improvements

## 🎓 Learning Path by Experience Level

### 🟢 Beginner (New to cybersecurity or datasets)
**Goal:** Understand what this tool does and how to use it safely
```
1. Read summary.md - Get the big picture
2. Follow install.md - Set up your environment  
3. Run test.py - Generate your first small dataset
4. Explore scenario.md - Understand what attacks were generated
```

### 🟡 Intermediate (Some cybersecurity background)
**Goal:** Generate datasets for specific research or learning objectives
```
1. Review analysis.md - Understand the features available
2. Check scenario.md - Plan which attacks you need
3. Customize config.json - Adjust durations for your needs
4. Run main.py - Generate full research datasets
```

### 🔴 Advanced (Cybersecurity professionals/researchers)
**Goal:** Modify, extend, or contribute to the framework
```
1. Study progress.md - Understand recent technical changes
2. Analyze analysis.md - Deep dive into feature engineering
3. Examine scenario.md - Understand attack implementations
4. Review source code - Modify or extend functionality
```

## 🛠️ Common Use Cases

### 🎓 **Educational Use**
- Teaching cybersecurity concepts
- Demonstrating attack patterns
- Learning SDN and OpenFlow
- Hands-on security exercises

### 🔬 **Research Applications**
- Training machine learning models
- Testing detection algorithms
- Studying attack evolution
- Benchmarking security systems

### 🏢 **Professional Development**
- Security team training
- Red team exercises
- Defense system validation
- Incident response practice

## 🆘 Getting Help

### 📖 **Check Documentation First**
- Most questions are answered in these docs
- Use the learning paths above to find relevant information
- Look for troubleshooting sections in each document

### 🐛 **For Technical Issues**
1. Check the log files in your output directory
2. Review the troubleshooting section in install.md
3. Ensure you're following the correct procedure for your experience level

### 💡 **For Feature Requests**
- Review progress.md to see if it's already planned
- Check if similar functionality exists in a different form
- Consider if it aligns with the framework's defensive security focus

## 🔒 Security Reminder

This framework is designed for **defensive security research and education only**. All generated attacks are contained within a virtual network environment and never touch real networks. Please use responsibly and in accordance with applicable laws and regulations.

## 📝 Documentation Conventions

- 🟢 **Green items** are beginner-friendly
- 🟡 **Yellow items** require some technical background
- 🔴 **Red items** are for advanced users
- 📊 **Data icons** indicate quantitative information
- ⚠️ **Warning icons** highlight important security or technical notes
- 💡 **Light bulb icons** provide helpful tips and best practices

---

**Ready to dive in? Start with [📖 Project Summary](summary.md) for the big picture, or jump to [⚙️ Installation Guide](install.md) if you're ready to get started!**