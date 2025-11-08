from mcp.server.fastmcp import FastMCP

mcp = FastMCP("google-calendar")

@mcp.tool('list-events')
def tool_list_events():
  pass