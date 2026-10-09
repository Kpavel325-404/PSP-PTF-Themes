# Contributing

Theme fixes, translations and real PSP test results are welcome.

1. Describe the affected theme and reproduce the problem. Use the supplied issue forms for display bugs or hardware results.
2. Edit the relevant source family under `sources/`. Build instructions are in [docs/BUILD.md](docs/BUILD.md).
3. Give an intentionally changed theme a new version, update `themes.json`, regenerate previews and checksums, and record the change in [CHANGELOG.md](CHANGELOG.md).
4. Run the verification tools. A pixel or checksum mismatch must be explained and resolved before replacing a released file.
5. Keep artwork provenance and component licences in [CREDITS.md](CREDITS.md). Original artwork contributions are preferred; include the source and reuse terms of contributed images.

Hardware reports should identify the exact PTF checksum, console model, firmware, language and observed behaviour. Preserve pending status for every untested model or step.
