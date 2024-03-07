# 0.0.5 (2024-03-05)

- Add /permanent-stream-url route
- Lock python version to `>=3.11,<3.12` for now (update to python >3.11 will be done in a dedicated PR)

# 0.0.4 (2023-04-03)

- Switch Docker base image from `python:3.11-alpine` to `python:3.11` (fix [#6](https://github.com/dailymotion/demo-stream-urls-server/issues/6))

# 0.0.3 (2023-03-24)

- Fix IP detection when running on both player and server on the same machine (using [ifconfig.me](https://ifconfig.me))
- Bump dependencies minimum version

# 0.0.2 (2023-03-23)

- Fix scope: replace "upload_videos read_videos edit_videos delete_videos" with "read_video_streams"
- Add CHANGELOG.md (never too late)

# 0.0.1 (2023-01-13)

First release
