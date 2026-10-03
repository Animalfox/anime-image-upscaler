# Contributing

Thanks for interest in **Anime Image Upscaler**.

## Development setup

Requirements: Python 3.12+, Make, and either [uv](https://github.com/astral-sh/uv) or pip.

```bash
make install
make up
```

Open the URL printed by `make up` (port is stored in `.port`).

Stop with:

```bash
make down
```

## Pull requests

1. Fork / branch from the default branch.
2. Keep changes focused — one concern per PR.
3. Update docs if behavior or setup steps change.
4. Describe what and why in the PR body.
5. Do not commit `.venv/`, `.port`, `.run/`, files under `data/uploads` /
   `data/outputs`, or extra model weight files beyond the bundled
   `weights/RealESRGAN_x4plus_anime_6B.pth`.

## Code style

- Prefer clear Python 3.12 typing.
- Match existing module layout under `app/`.
- UI strings live in `app/static/i18n.js` (English default, optional Russian).
- API error strings live in `app/i18n.py` and follow `Accept-Language`.
- README and community docs stay in English.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reports. Do not open public issues for security problems.

## License

By contributing, you agree that your contributions are licensed under the MIT License (`LICENSE`). Model weights remain under their own terms (`NOTICE`).
