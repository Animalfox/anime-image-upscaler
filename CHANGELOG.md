# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-03

### Added

- Local FastAPI web UI for 4× anime upscaling with RealESRGAN Anime 6B
- Bundled model weights under `weights/` (BSD-3-Clause; see NOTICE)
- Make lifecycle: `install` / `up` / `down`
- English default UI/API with Russian locale auto-detect
- GitHub community files, CI (Ruff + syntax), Dependabot

### Security

- Validate download `job_id` to prevent path traversal
- Keep upscale error details in the server log only
- Cap input image long side at 4096px

### Changed

- Animalfox sticker-pack UI, before/after compare slider
- README media kept in-repo under `docs/assets/`
