# OS Guardian

The OS Guardian coordinates system automation under strict policy control. It consists of four building blocks:

1. **Perception** – captures the screen and detects interface elements using optional OpenCV and YOLO models.
2. **Action engine** – wraps `pyautogui`, shell commands and Selenium to perform mouse, keyboard and browser actions.
3. **Planning** – converts natural language instructions into ordered tool calls via a small LangChain agent and vector memory.
4. **Safety** – checks permissions for commands, domains and applications while tracking undo callbacks.

These modules can be invoked individually or through the ``os-guardian`` command line interface.

## Policy File

Permissions may also be configured in a YAML policy referenced by the
``OG_POLICY_FILE`` environment variable. The file supports allowlists and simple
rate limits:

```yaml
policy: ask                        # allow, ask or deny actions
allowed_commands:
  - echo
  - ls
command_limits:
  rm:
    max: 1                         # once per day
    window: 86400                  # seconds
allowed_domains:
  - example.com
domain_limits:
  example.com:
    max: 5                         # five visits per hour
    window: 3600
```

Set ``OG_POLICY_FILE=/path/to/policy.yaml`` before launching the tools so the
safety module can enforce these limits.

## Environment variables

The safety layer also reads the following variables:

- ``OG_POLICY`` – default permission mode: ``allow``, ``ask`` or ``deny``.
- ``OG_ALLOWED_COMMANDS`` – colon‑separated list of shell commands that may run.
- ``OG_ALLOWED_APPS`` – colon‑separated list of application paths.
- ``OG_ALLOWED_DOMAINS`` – colon‑separated list of domains permitted in
  ``open_url``.

These overrides are merged with any values found in the policy file.
See [os_guardian_permissions.md](os_guardian_permissions.md) for a full
explanation of the safety framework.

