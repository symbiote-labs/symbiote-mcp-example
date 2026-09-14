# Symbiote MCP example

A local Python tool you can call from Symbiote chat. It takes a name and returns
`Hello, <name>!`.

Run the MCP server and CLI on your computer. The CLI's microagent connects to
Symbiote and forwards tool calls back here for execution.

## Install

The MCP server needs **Python 3.11+** and **FastMCP `>=3.2,<4`** in its runtime
environment. The setup below installs FastMCP for you. The working example uses
Python 3.12.12 and FastMCP 3.4.7; the dependency versions are recorded in `uv.lock`.
These requirements apply to the MCP server; the standalone Symbiote CLI bundles
its own runtime.

On macOS or Linux, install the [Symbiote CLI](https://github.com/symbiote-labs/symbiote-cli-dist):

```sh
curl -fsSL https://raw.githubusercontent.com/symbiote-labs/symbiote-cli-dist/main/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
symbiote --profile demo version
```

With Git and [uv](https://docs.astral.sh/uv/getting-started/installation/) installed:

```sh
git clone https://github.com/symbiote-labs/symbiote-mcp-example.git
cd symbiote-mcp-example
uv sync --locked --python 3.12
```

## Log in

Use your Symbiote server URL and sign in through the browser:

```sh
symbiote --profile demo login --server https://symbiote.example.com --agent-path /agent
symbiote --profile demo status
```

`demo` is a local profile name. Use the same profile in the commands below.
The `/agent` option depends on your server's routing; omit it for a direct
agent endpoint. Ask your administrator for the correct URL and prefix.

## Connect your local tool

```sh
cp agent-config.example.yaml agent-config.yaml
uv run python -c 'import shutil; print(shutil.which("symbiote-hello-world"))'
```

Paste the printed executable path into `command` in `agent-config.yaml`:

```yaml
agent:
  name: hello-world

mcp_servers:
  example:
    type: stdio
    command: '"/your/checkout/.venv/bin/symbiote-hello-world"'

allowed_paths: []
```

Keep the inner double quotes for paths with spaces. Use an absolute path;
`~` and `$HOME` are not expanded here.

```sh
symbiote --profile demo microagent start --config agent-config.yaml
```

You should see `Discovered 1 tool(s)` followed by `Connected`. Leave this
terminal running. The CLI starts the MCP server for you.

## Try it in chat

In another terminal, check that `hello-world` is connected with one tool:

```sh
symbiote --profile demo microagent status --json
```

Open Symbiote chat, sign in with the same account as the CLI, and send:

> Call `hello-world:example_hello_world` through `microagent_call_tool` with
> `name` set to `World`. Show the actual tool result.

Expected result: `Hello, World!`

Or send the chat request from a second local terminal:

```sh
symbiote --profile demo query 'Call hello-world:example_hello_world through microagent_call_tool with name "World". Show the actual tool result.' --json
```

Look for a `microagent_call_tool` call and a successful tool result containing
`Hello, World!`. The chat response alone isn't proof that the tool ran.

Stop the proxy with Ctrl+C. Restart it after adding or changing tools.
If the connection drops, run the start command again.

## Run in your own environment

Run the microagent on a computer that can reach Symbiote and the system your
integration uses. Set `command` to start your MCP server with the dependencies
and environment it needs. This can be an installed executable or a launcher
script; use absolute paths.

See [Studio packaging](STUDIO_PACKAGING.md) for Rez, Conda, and container setups.

The microagent's tools belong to the Symbiote account it logs in with. Another
user's chat does not automatically have access to them.

## Make it yours

Edit [the server](src/symbiote_mcp_example/__init__.py). Replace the greeting
with a call to your API, or add another `@mcp.tool()` function. Types and
docstrings describe the inputs to Symbiote. Prefix tool names for your
integration to avoid collisions.

Return text or JSON-serializable data. Keep stdout for MCP; use a log file for
debugging, since the microagent discards stderr.
[FastMCP's guide](https://gofastmcp.com/servers/tools) covers tool authoring.

Run the local tests:

```sh
uv run python -m unittest discover -s tests -v
```

If discovery finds zero tools, check the executable path and run the tests.
If chat can't reach the tool, check the account, profile, and proxy terminal.
If the session expires, log in again and restart the proxy.
