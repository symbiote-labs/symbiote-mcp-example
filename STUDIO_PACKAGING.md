# Studio packaging

Use your studio's existing environment tools. The microagent only needs a
command that starts an MCP server and keeps stdin/stdout connected.

The CLI runs on a workstation or service host with access to Symbiote and your
API. Your server runs there too, with its own dependencies. Login and the chat
test stay the same as in the [README](README.md).

The MCP server's runtime environment must provide **Python 3.11+** and
**FastMCP `>=3.2,<4`**, including FastMCP's dependencies and your API libraries.
The working example uses Python 3.12.12 and FastMCP 3.4.7. The standalone
Symbiote CLI bundles its own runtime; installing it does not supply Python or
FastMCP to your MCP server.

## Which option fits?

| Your setup | Launch the MCP server with |
| --- | --- |
| Python tools with a virtual environment | The installed executable, as in the README |
| Versioned studio packages managed by Rez | `rez env` |
| Conda or micromamba environments | The environment manager's `run` command |
| Containerized services | `docker run -i` |

Rez has documented use across VFX studios ([ASWF](https://tac.aswf.io/meetings/2026-04-29/2026-04-29.html)).
The other options below are alternatives for particular environments, not a
ranking of studio adoption.

All paths and package names below are examples. The shell recipes target
Linux/macOS; use your platform's launcher conventions on Windows.

## Rez

If you already package Python tools with Rez, package the MCP server the same
way, with the runtime requirements above.

For this example, a minimal installed package could look like:

```text
/studio/packages/symbiote_hello_world/0.1.0/
  package.py
  bin/symbiote-hello-world
  python/symbiote_mcp_example/__init__.py
```

Copy `src/symbiote_mcp_example` from this repo into `python/`. Define `package.py`:

```python
name = "symbiote_hello_world"
version = "0.1.0"
requires = ["python-3.12", "fastmcp-3.2+<4"]
tools = ["symbiote-hello-world"]


def commands():
    env.PATH.prepend("{root}/bin")
    env.PYTHONPATH.prepend("{root}/python")
```

Those dependency names assume your studio provides matching Rez packages,
including FastMCP's dependencies. Adjust them to your repository. Rez will not
download them from PyPI just because they appear in `requires`.

Create `bin/symbiote-hello-world` and make it executable:

```python
#!/usr/bin/env python
from symbiote_mcp_example import main

main()
```

Put the installed package in your configured Rez search path, using your
studio's usual release process. For this layout, the search path contains
`/studio/packages`, not the individual package's version directory.
The layout above describes the installed result; this repository does not
provide a `rez-build` recipe.

In `agent-config.yaml`, replace the MCP server's `command`:

```yaml
command: '"/path/to/rez" env -q --norc symbiote_hello_world-0.1.0 -- symbiote-hello-world'
```

The CLI launches the server inside the resolved environment. It does not need
to run inside that environment itself. `-q --norc` reduces shell startup output;
your package commands and launcher must also leave stdout clean.

See Rez's [package definitions](https://rez.readthedocs.io/en/stable/package_definition.html),
[environment commands](https://rez.readthedocs.io/en/stable/package_commands.html),
and [`rez env` reference](https://rez.readthedocs.io/en/stable/commands/rez-env.html).

## Conda or micromamba

Install the integration into a dedicated environment. For example, from this
checkout, with Conda already installed:

```sh
conda create -y -p /path/to/mcp-env python=3.12 pip
conda run -p /path/to/mcp-env python -m pip install .
```

Then configure:

```yaml
command: '"/path/to/conda" run --no-capture-output -p "/path/to/mcp-env" symbiote-hello-world'
```

Conda's [`--no-capture-output`](https://docs.conda.io/projects/conda/en/stable/commands/run.html)
keeps MCP messages flowing through the pipes.

For an integration already installed in a micromamba environment:

```yaml
command: '"/path/to/micromamba" run -p "/path/to/mcp-env" symbiote-hello-world'
```

Using [`run`](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html)
avoids relying on an interactive shell's activation state.

## Containers

If your studio distributes tools as images, build an image containing the
installed integration and its dependencies. With an image that accepts a
command to run:

```yaml
command: '"/path/to/docker" run --rm -i --pull=never studio-mcp:0.1.0 symbiote-hello-world'
```

Pull or load the image before starting the proxy. Add the mounts, network
access, and credentials your API needs. Use a container for tools that can run
there; it does not automatically gain access to a desktop application's Python.

[`-i` keeps stdin open](https://docs.docker.com/reference/cli/docker/container/run/).
Do not add `-t` or `-d`: MCP needs ordinary pipes and an attached process.

## Existing launchers and application plugins

A studio launcher script can be the `command` too. It should set up the
environment and run the MCP server in the foreground. On POSIX shells, use
`exec` for the final command so signals reach the server.

Application-specific systems, such as
[Houdini packages](https://www.sidefx.com/docs/houdini/ref/plugins.html), configure
plugins inside that application. Keep using them where needed; they do not
replace the MCP server or microagent.

Whichever option you choose, install dependencies before startup, keep stdout
for MCP messages, and repeat the README's discovery and chat test using the
actual deployment command. Restart the proxy after updating its tools.
