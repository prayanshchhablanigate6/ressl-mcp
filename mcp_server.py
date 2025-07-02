import logging
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from minio_utils import (
    read_file_from_minio,
    write_file_to_minio,
    delete_file_from_minio,
    create_file_in_zip_in_minio,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

mcp = FastMCP("RESSL-MCP Server")

class EditFileParams(BaseModel):
    zip_filename: str = Field(..., description="The name of the ZIP file in MinIO.")
    file_path: str = Field(..., description="Path to the file inside the ZIP.")
    new_content: str = Field(..., description="New content to overwrite the file with.")

class CreateFileParams(BaseModel):
    zip_filename: str = Field(..., description="The name of the ZIP file in MinIO.")
    file_path: str = Field(..., description="Path to the file inside the ZIP.")
    content: str = Field("", description="Content to write to the new file.")

class DeleteFileParams(BaseModel):
    zip_filename: str = Field(..., description="The name of the ZIP file in MinIO.")
    file_path: str = Field(..., description="Path to the file inside the ZIP.")

@mcp.tool(description="Edit (overwrite) a file inside a ZIP in MinIO.")
def edit_file(params: EditFileParams) -> str:
    print("I am parrams of edit: ", params)
    """Overwrite the file with new content inside the ZIP."""
    try:
        write_file_to_minio(params.zip_filename, params.file_path, params.new_content)
        return "OK"
    except Exception as e:
        logger.error(f"Error editing file: {e}")
        raise

@mcp.tool(description="Create a new file inside a ZIP in MinIO (if it does not exist).")
def create_file(params: CreateFileParams) -> str:
    print("I am parrams of create: ", params)

    """Create a new file with optional content inside the ZIP. Does not overwrite if exists."""
    try:
        create_file_in_zip_in_minio(params.zip_filename, params.file_path, params.content)
        return "OK"
    except Exception as e:
        logger.error(f"Error creating file: {e}")
        raise

@mcp.tool(description="Delete a file from a ZIP in MinIO.")
def delete_file(params: DeleteFileParams) -> str:
    print("I am parrams of delete: ", params)

    """Delete a file from inside the ZIP."""
    try:
        delete_file_from_minio(params.zip_filename, params.file_path)
        return "OK"
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise

app = mcp.http_app(stateless_http=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_async("streamable-http", host="0.0.0.0", port=3000)) 