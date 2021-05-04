# webtools-Fitbit4Food

forked from <https://github.com/djshan1979/webtools-Fitbit4Food>

> Purpose was just to improve the project a bit and figure out, which apt packages are really needed

## Improvements

- linting all python files
- sorting imports in all python files
- stripped down `packages.txt` to only required apt packages
- added `Dockerfile`
- added `docker-compose.yml`
- added `.gitignore`
- added `.dockerignore`
- added `.streamlit/config.toml`
- added `.flake8`
- added `.env`

## Packages

The only required packages in `packages.txt` seems to be:

```txt
tesseract-ocr
```

## Docker

To test out the streamlit app locally with docker just run:

```shell
docker compose build
docker compose up
```

and open the streamlit app in <http://localhost:8501/>
