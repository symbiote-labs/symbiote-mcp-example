"""Exercise the installed server through real MCP pipes, without Symbiote or mocks."""

import shutil
import unittest

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

TOOL_NAME = "example_hello_world"


class StdioTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        command = shutil.which("symbiote-hello-world")
        self.assertIsNotNone(command, "Install the project before running the tests")
        self.client = Client(StdioTransport(command=command, args=[]), timeout=10)
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.__aexit__, None, None, None)

    async def test_discovery_advertises_one_tool_and_its_name_parameter(self) -> None:
        tools = await self.client.list_tools()

        self.assertEqual([tool.name for tool in tools], [TOOL_NAME])
        self.assertTrue(tools[0].description)
        self.assertEqual(tools[0].inputSchema["properties"]["name"]["type"], "string")
        self.assertEqual(tools[0].inputSchema["required"], ["name"])

    async def test_call_returns_the_supplied_name_over_stdio(self) -> None:
        result = await self.client.call_tool(TOOL_NAME, {"name": "Zoë — local MCP"})

        self.assertEqual(result.content[0].text, "Hello, Zoë — local MCP!")
        self.assertFalse(result.is_error)

    async def test_invalid_arguments_return_an_error_and_server_remains_usable(self) -> None:
        for arguments in ({}, {"name": {"invalid": "object"}}):
            with self.subTest(arguments=arguments):
                result = await self.client.call_tool(TOOL_NAME, arguments, raise_on_error=False)
                self.assertTrue(result.is_error, f"Expected validation failure for {arguments!r}")

        result = await self.client.call_tool(TOOL_NAME, {"name": "World"})
        self.assertEqual(result.content[0].text, "Hello, World!")


if __name__ == "__main__":
    unittest.main()
