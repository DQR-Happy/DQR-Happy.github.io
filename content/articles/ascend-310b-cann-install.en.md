## Scope and recorded environment

This note revisits my [July 2026 installation record](https://blog.csdn.net/ruiqideng/article/details/163346232) for an Orange Pi AI Pro with an Ascend 310B1 NPU and CANN 9.0.1. The original records an `aarch64` machine, installer success messages, and an environment variable check. It does not identify the OS image, driver and firmware versions, or provide a complete installation log.

Although the original lists an ACL Python device check as a goal, it does not include the command or its result. It also excludes sample compilation and custom-operator tests. This is therefore an installation account, not proof that an operator or an ACL application ran successfully. The setup has not been reproduced for this English revision.

## Identify the device and installation state

On the recorded board, `uname -m` reported `aarch64`, and `npu-smi info` identified the device as 310B1. Before selecting packages on a different system, check the device, OS and kernel, installed driver and firmware, and the release-specific compatibility information:

```bash
uname -m
uname -r
npu-smi info
```

A successful `npu-smi` query is useful evidence that the driver can report the device; it does not validate CANN, ACL, or custom operators. A failure should be investigated before assuming the toolkit is at fault.

## Prepare the prerequisites

The original used an apt-based system and installed `gcc`, `python3`, and `python3-pip`. Those packages are not a complete, universal dependency list: check the CANN version and board-specific requirements before installation. It also notes that a vendor kernel may not have a matching `linux-headers-$(uname -r)` package in the default repository. Whether headers are required depends on the installation and driver work being performed; do not assume they can always be skipped.

The original mentions creating the `HwHiAiUser` account and group when absent. Its displayed `useradd` command omits the username, so it should not be copied as a working command. Check the release-specific installation instructions and existing system accounts before making account or driver changes.

## Install the recorded packages

The recorded filenames were `Ascend-cann_9.0.1_linux-aarch64.run` and `Ascend-cann-310b-ops_9.0.1_linux-aarch64.run`. The combined package and the 310B ops package were installed under `/usr/local/Ascend` using `--install`; the original shows success summaries for both. These are historical filenames and results, not a claim that the same files or instructions apply to a later release.

The combined package can include both driver and Toolkit components; it must not be treated as a Toolkit-only installer. The [CANN 9.0.x parameter reference](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/900/softwareinst/instg/instg_0043.html) describes the combined package and its `--whitelist` options. Consult the exact version's installation guide and board vendor's compatibility guidance before changing an existing driver. Install the matching device-specific ops package in the appropriate path, and verify package integrity using the vendor-provided method.

## Load the environment and check what was observed

After installation, the original sourced the environment script in the current shell:

```bash
source /usr/local/Ascend/cann/set_env.sh
printf '%s\n' "$ASCEND_HOME_PATH"
```

The recorded output was `/usr/local/Ascend/cann-9.0.1`. This indicates that the variable was set in that shell; it does not establish that libraries load correctly or that inference works. The installation path and script location may differ for a non-root or custom-path installation. The [Ascend installation guide](https://www.hiascend.com/doc_center/source/en/CANNCommunityEdition/910/softwareinst/instg/instg_0008.html) likewise distinguishes the installation path and current-shell environment; it is for a newer release, so use the 9.0.x guide for version-specific decisions.

A stronger follow-up would record the image and all component versions, verify the package and driver compatibility, and run a documented device or ACL sample with its command and output. Those checks were not captured in the source and are not reported here as completed.
