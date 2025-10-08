# AI Coding Agent Instructions

## Architecture Overview

This is an **MCP (Model Context Protocol) server** that exposes Azure AI Vision Face API as tools for AI agents. The server uses **FastMCP** framework to register Python functions as MCP tools with automatic schema generation from Pydantic type annotations.

**Key Components:**
1. **MCP Server** (`src/mcpServer.py`): FastMCP server that registers 13+ face detection/recognition tools
2. **Tool Functions** (`src/tools/*.py`): Individual Azure Face API operations (detect, compare, enroll, identify, etc.)
3. **Tool Descriptors** (`src/tools/utils/_enums.py`): Configuration classes containing tool names, descriptions, and parameter instructions for AI agents
4. **Prompt Utilities** (`src/prompt_utils/`): Optional parsers and dispatchers for natural language prompts (used in testing)

**Data Flow:**
AI Agent → MCP Protocol (stdio) → FastMCP Server → Azure Face API → Response → AI Agent

## Environment Setup

**Three credential approaches:**
1. **MCP Mode (VS Code)**: Credentials in `.vscode/mcp.json` using input prompts (rename `.vscode/mcp-bp.json`)
2. **Local Testing**: Copy `.env.example` to `.env` with real credentials for pytest
3. **CI/CD**: GitHub repository secrets `AZURE_FACE_ENDPOINT` and `AZURE_FACE_API_KEY`

**Required credentials:**
- `AZURE_FACE_ENDPOINT` and `AZURE_FACE_API_KEY` (mandatory)
- `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` (optional, for open-set attribute detection)
- `AZURE_STORAGE_ACCOUNT`, `AZURE_STORAGE_CONTAINER`, `AZURE_STORAGE_SAS_TOKEN` (optional, for blob storage)

## Running the Server

**Via VS Code GitHub Copilot:**
1. Configure `.vscode/mcp.json` with credentials
2. Press "Start" in the JSON file above `azure_ai_vision_face_api_mcp_server`
3. Use `@azure_ai_face_api` in Copilot chat to invoke tools

**Direct invocation (for testing):**
```bash
uvx --from git+https://github.com/Azure-Samples/azure-ai-vision-face-api-mcp-server azure-face-mcp
```

**HTTP Bridge (Node/TypeScript for web apps):**
```bash
cd bridge && npm install && npm run dev  # Exposes REST API on port 8787
```

## Testing

**Run live tests:**
```bash
cd /path/to/repo
uv venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .
pytest -v  # Requires .env with real credentials
```

**Test structure:**
- `tests/conftest.py`: Validates credentials aren't placeholders before running live tests
- `test_prompt_live_*.py`: End-to-end tests using prompt parsing
- `test_prompt_parsers.py`: Unit tests for prompt parsing logic
- Example images in `example/` folder (detection1.jpg, reco/Alice, etc.)

## Project-Specific Patterns

### Tool Function Signatures
All tool functions use **Pydantic `Annotated` with `Field(description=...)`**:
```python
def enroll_face_to_group(
    file_path_list: Annotated[str, Field(description=EnrollFaceToLPGConfig.ARGS_FILE_PATH_LIST)],
    person_name: Annotated[str, Field(description=EnrollFaceToLPGConfig.ARGS_PERSON_NAME)],
    group_uuid: Annotated[str, Field(description=EnrollFaceToLPGConfig.ARGS_GROUP_UUID)],
    is_url: Annotated[bool, Field(description=EnrollFaceToLPGConfig.ARGS_IS_URL)] = False
)
```
The `description` strings contain **instructions for AI agents** (e.g., "YOU (MCP) must ask the user...").

### Large Person Group (LPG) Workflow
Face recognition requires a **multi-step enrollment process**:
1. `create_large_person_group()` → Returns `group_uuid`
2. `enroll_face_to_group(file_path_list, person_name, group_uuid)` → Returns `person_id`
3. `identify_face_from_group(file_path, group_uuid)` → Matches against enrolled faces

**Critical:** After enrolling faces, the LPG must be **trained** (handled automatically by Azure SDK).

### URL vs Local File Handling
Most tools accept both local paths and URLs:
- Check `is_url` parameter (default: `False`)
- Local paths: Use `os.path.exists()` validation, read with `open(file_path, 'rb')`
- URLs: Use `face_client.detect_from_url()` directly
- **Azure Blob URLs:** Automatically append SAS token in `list_public_image_urls()` (see `src/tools/BlobFolderTools.py`)

### Deletion Safety Pattern
Deletion functions use **double-confirmation** instructions in descriptions:
```python
DeletePersonFromLPGConfig.TOOL_DESC = "... YOU (MCP) must double confirm with the user before proceeding..."
```
AI agents must explicitly warn users about irreversibility.

### Two-Stage Attribute Detection
1. **Fixed attributes** (`AzureFaceAttrib.py`): Azure Face API's built-in attributes (age, mask, glasses, blur, etc.)
2. **Open-set attributes** (`OpensetFaceAttrib.py`): Uses GPT-4V to analyze arbitrary attributes (hair color, clothing, etc.) by cropping face bounding boxes and sending to OpenAI

### Face Comparison Modes
`compare_source_image_to_target_image()` supports three modes:
- `largest_face`: Compare only largest faces in each image
- `most_similar`: Find best match for each source face using `find_similar` API
- `exhaustive`: Compare all faces in both images pairwise

**AI agents must explain these modes to users** (enforced via tool description).

## Integration Points

**Azure Face API:**
- All tools use `FaceClient` from `azure.ai.vision.face` SDK
- Detection model: `DETECTION03`, Recognition model: `RECOGNITION04`
- Custom telemetry header: `X-MS-AZSDK-Telemetry: sample=mcp-face-*`

**OpenAI (optional):**
- Used only for open-set attribute detection via GPT-4V
- Requires `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`
- API version: `2025-03-01-preview`

**Azure Blob Storage (optional):**
- Provides centralized image storage
- `list_blob_folders_and_choose()`: Lists top-level folders
- `list_public_image_urls()`: Returns URLs with SAS tokens appended
- `download_blob_folder_from_container()`: Downloads entire folder to local filesystem

**MCP Protocol:**
- Transport: stdio (stdin/stdout)
- FastMCP auto-generates tool schemas from function signatures
- Server name: `azure_ai_face_api`
- Entry point: `mcpServer:run_server` in `pyproject.toml`

## Key Files & Directories

- `src/mcpServer.py`: Main server class, tool registration
- `src/tools/utils/_enums.py`: Tool configurations with AI agent instructions
- `src/tools/*.py`: Individual tool implementations
- `.vscode/mcp-bp.json`: MCP server configuration template
- `example/`: Sample images for testing (detection1.jpg, reco/Alice, reco/Bob)
- `bridge/server/mcp-bridge.ts`: HTTP REST API wrapper for web integration
- `tests/conftest.py`: Credential validation logic for live tests

## Common Gotchas

1. **Placeholder credentials fail silently**: `conftest.py` checks for `<`, `example`, `REPLACE` markers
2. **LPG training latency**: Face recognition may take 10-20 seconds after enrollment
3. **File path resolution**: Tests use `_find_file_upwards()` to locate example images
4. **URL detection in prompts**: Regex patterns in `prompt_parser.py` expect `http://` or `https://`
5. **SAS token handling**: Always use `list_public_image_urls()` for blob URLs (manual URLs may lack SAS)
