from tools.cuisine_tool import CuisineSearchTool


class ToolRegistry:
    def __init__(self):
        self.tools = {
            "cuisine_search": CuisineSearchTool()
        }

    def call(self, tool_name: str, input_data: dict):
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        return self.tools[tool_name].run(input_data["query"])