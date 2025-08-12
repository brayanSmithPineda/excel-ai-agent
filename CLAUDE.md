# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

### Before starting work
- Always in plan mode to make a plan
- After get the plan, make sure you Write the plan to .claude/tasks/TASK_NAME.md.
- The plan should be a detailed implementation plan and the reasoning behind them, as well as tasks broken down.
- If the task require external knowledge or certain package, also research to get latest knowledge (Use Task tool for research)
- Don't over plan it, always think MVP.
- Once you write the plan, firstly ask me to review it. Do not continue until I approve the plan.

### Microsoft Standards Compliance

**MANDATORY: Always consult Microsoft official documentation BEFORE implementing any feature**

Before building any component, feature, or integration, you MUST:

1. **Check Microsoft Official Docs First**: Always start by researching Microsoft's official documentation for the specific area you're working on:
   - **Frontend/UI**: [Office Add-ins documentation](https://docs.microsoft.com/en-us/office/dev/add-ins/) and [Fluent UI React Components](https://react.fluentui.dev/) (Microsoft's recommended UI framework for Office applications)
   - **Excel Integration**: [Excel JavaScript API reference](https://docs.microsoft.com/en-us/javascript/api/excel)
   - **Office.js**: [Office JavaScript API documentation](https://docs.microsoft.com/en-us/office/dev/add-ins/reference/javascript-api-for-office)
   - **Manifest**: [Office Add-ins manifest documentation](https://docs.microsoft.com/en-us/office/dev/add-ins/develop/add-in-manifests)
   - **Authentication**: [Office Add-ins authentication patterns](https://docs.microsoft.com/en-us/office/dev/add-ins/develop/auth-overview)

2. **Follow Microsoft Recommendations**: Use Microsoft's recommended tools, patterns, and best practices:
   - **UI Framework**: Use Fluent UI React Components for consistent Office experience
   - **Development Tools**: Use Office Add-ins Yeoman generator and recommended project structure
   - **Design System**: Follow Fluent Design principles and Office design guidelines
   - **Performance**: Implement Microsoft's performance optimization recommendations

3. **Document Compliance**: When implementing features, document:
   - Which Microsoft documentation guided your implementation
   - Why you followed specific Microsoft recommendations
   - Any deviations from Microsoft standards (with justification)

4. **Exception Process**: If you believe we should deviate from Microsoft recommendations:
   - **Clearly state the Microsoft recommendation we're deviating from**
   - **Provide specific technical reasons for the deviation**
   - **Document potential risks and mitigation strategies**
   - **Get explicit approval for the deviation**

**Examples of Microsoft-First Approach:**
- ✅ Using Fluent UI React Components for consistent Office UI experience
- ✅ Following Office Add-ins manifest schema and best practices
- ✅ Implementing Microsoft's recommended authentication patterns
- ✅ Using Office.js APIs as documented in official Microsoft docs
- ❌ Using a custom UI framework without checking Microsoft recommendations first
- ❌ Implementing authentication patterns without consulting Office Add-ins auth docs

**Key Microsoft Documentation Resources:**
- [Office Add-ins platform overview](https://docs.microsoft.com/en-us/office/dev/add-ins/overview/office-add-ins)
- [Fluent UI React Components](https://react.fluentui.dev/)
- [Office JavaScript API reference](https://docs.microsoft.com/en-us/javascript/api/overview/office)
- [Office Add-ins best practices](https://docs.microsoft.com/en-us/office/dev/add-ins/concepts/add-in-development-best-practices)

This ensures our Excel AI Agent follows Microsoft's established patterns and provides the best possible user experience within the Office ecosystem.

### While implementing
- You should update the plan as you work.
- After you complete tasks in the plan, you should update and append detailed descriptions of the changes you made, so following tasks can be easily hand over to other engineers.
- Add comprehensive comments explaning every single line of code, import, and decision.

### Session Management Workflow
**STARTING A NEW SESSION:**
1. Read .claude/SESSION_STATE.md to understand current progress
2. Read .claude/ANALYSIS_GUIDE.md if analyzing existing code
3. Check .claude/tasks/*.md files for implementation plans
4. Continue where previous session left off

**ENDING A SESSION:**
1. Update .claude/SESSION_STATE.md with current progress
2. Update implementation plans with completed tasks
3. Note any important findings or blockers
4. Ensure all code has comprehensive comments

## Project Overview

Excel AI Agent is a Microsoft Excel add-in that serves as a secure, auditable, and governed AI copilot for Excel users, particularly targeting finance teams in mid-market companies. The project uses a hybrid architecture with a Python FastAPI backend and a TypeScript/React Excel add-in frontend.

## Architecture

The project follows a client-server architecture:

- **Backend**: Python FastAPI application handling AI integration (Anthropic Claude), data processing, business tool integrations (Stripe, NetSuite, Notion, Metabase), security controls, and audit logging
- **Frontend**: TypeScript/React Excel add-in using Office.js for Excel integration, providing chat interface, task panes, and data preview modals
- **Communication**: REST API with JWT authentication between add-in and backend, WebSockets for real-time progress updates
- **Security**: Granular access controls (row/column permissions), full audit logging, data preview before cloud transmission

## Office JavaScript API Requirements

**Complete Requirement Sets Configuration:**

Our Excel AI Assistant add-in uses multiple Office JavaScript API requirement sets to enable comprehensive functionality:

### **Requirement Sets:**
- **ExcelApi 1.3** - Core Excel functionality: worksheets, ranges, tables, data manipulation
- **IdentityApi 1.3** - Authentication and identity management for JWT auth with backend  
- **DialogApi 1.2** - Dialog boxes for authentication flows and user confirmations
- **SharedRuntime 1.1** - Shared runtime for persistent state and WebSocket connections

### **Individual Methods:**
- **Office.context.document.settings.saveAsync** - Store user preferences and auth tokens
- **Office.context.document.settings.refreshAsync** - Reload stored settings
- **Office.context.ui.displayDialogAsync** - Show authentication and confirmation dialogs
- **Office.context.ui.messageParent** - Communicate between dialogs and main add-in

### **Platform Support:**
- **Office 2016+** and **Microsoft 365** (all requirement sets supported)
- **Excel on the Web** (full compatibility)
- **Excel on iPad/Mac** (varies by specific version)

### ⚠️ IMPORTANT: Feature Development Guidelines

**EVERY TIME you add a new Office feature to the add-in, you MUST:**

1. **Check API Compatibility**: Visit [Office JavaScript API requirement sets](https://docs.microsoft.com/en-us/office/dev/add-ins/reference/requirement-sets/) to verify the minimum API version required for your new feature.

2. **Update Requirement Sets**: If your feature requires a higher API version or new requirement set, update the `<Requirements>` section in `frontend/ExcelAIAgent/manifest.xml`:
   ```xml
   <Requirements>
     <Sets DefaultMinVersion="1.1">
       <Set Name="ExcelApi" MinVersion="1.3"/>
       <Set Name="IdentityApi" MinVersion="1.3"/>
       <Set Name="DialogApi" MinVersion="1.2"/>
       <Set Name="SharedRuntime" MinVersion="1.1"/>
       <!-- Add new requirement sets here -->
     </Sets>
     <Methods>
       <!-- Add new individual methods here -->
       <Method Name="Office.context.document.settings.saveAsync"/>
     </Methods>
   </Requirements>
   ```

3. **Document the Change**: Update this section in CLAUDE.md with the new requirements and explain why they were necessary.

4. **Test Compatibility**: Ensure the add-in still works on the intended Office versions after adding new requirements.

**Current API Coverage:**
- **Excel Operations**: ExcelApi 1.3 (worksheets, ranges, tables, data manipulation)
- **Authentication**: IdentityApi 1.3 (JWT flows, token management)
- **User Interactions**: DialogApi 1.2 (auth dialogs, confirmations, data preview)
- **Persistent State**: SharedRuntime 1.1 (WebSocket connections, chat history)
- **Settings Storage**: Individual methods for preferences and tokens

**Common Additional Requirements:**
- **OpenBrowserWindowApi 1.1**: For OAuth redirects to external browser
- **RibbonApi 1.1**: For dynamic ribbon customization
- **ExcelApi 1.4+**: For advanced data analysis features
- **ExcelApi 1.7+**: For custom functions
- **ExcelApi 1.11+**: For co-authoring features

This ensures our add-in maintains compatibility while supporting the features we implement.

## Development Setup

This project uses Poetry for Python dependency management:

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Add dependencies
poetry add package_name

# Add development dependencies
poetry add --group dev package_name
```

## Key Requirements

- Python >=3.13
- Node.js (for Excel add-in development)
- Poetry for Python package management
- Office.js for Excel integration
- React/TypeScript for frontend UI
- PostgreSQL for production database
- SQLite for development/testing

## Project Structure (Planned)

- `backend/` - Python FastAPI application
- `frontend/` - TypeScript/React Excel add-in
- `docs/` - Documentation and API specifications

## Core Features Implementation Priority

1. Data cleaning engine (duplicate detection, format standardization, missing value handling)
2. Security and governance layer (access controls, audit logging)
3. Claude AI integration for intelligent assistance
4. Business tool integrations starting with Stripe
5. Excel UI components (task pane, chat interface, settings panel)

## Security Considerations

This project emphasizes security-first approach:
- All AI interactions must be logged for audit purposes
- Granular access controls at sheet/column level
- Data preview system before any cloud transmission
- Option for self-hosted LLM deployment
- JWT-based authentication between components