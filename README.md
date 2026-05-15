# English Listening GitHub Pages

This folder is ready to upload to a public GitHub repository and serve with GitHub Pages.

## Files

- `index.html`: student player. It loads article JSON files from `articles/`.
- `admin.html`: online admin generator. It calls a local TTS server at `http://127.0.0.1:5000/tts`.
- `articles/`: exported article JSON files.
- `tts_server.py`: local Edge TTS backend. It only provides `POST /tts`.

## Local TTS Server

Install the dependency once:

```powershell
py -m pip install edge-tts
```

Start the server:

```powershell
py tts_server.py
```

The admin page sends:

```json
{ "text": "Sentence to synthesize." }
```

The server returns:

```json
{ "audio": "data:audio/mpeg;base64,..." }
```

## Publishing Workflow

1. Upload this folder's contents to a public GitHub repository.
2. Enable GitHub Pages for the repository.
3. Open `admin.html` from the GitHub Pages URL.
4. Start `tts_server.py` locally.
5. Generate audio and export the article JSON.
6. Upload the exported JSON into the repository's `articles/` folder.
7. Open `index.html`; the new article appears in `选择文章`.

## Local Preview

For a local static preview, run a static server from this folder:

```powershell
py -m http.server 8000
```

Then open:

- `http://127.0.0.1:8000/admin.html`
- `http://127.0.0.1:8000/index.html`

If `py -m http.server` is not available, any static file server is fine.
