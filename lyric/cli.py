import typer
from scraper import fetch_lyrics, fetch_songs

app = typer.Typer(help="Lyric related commands")


@app.command(name="fetch-lyric")
def select_song(
    query: str,
    output: str = typer.Option(None, "--output", "-o", help="File to write results to"),
):
    results = fetch_songs(query)

    for i, result in enumerate(results, 1):
        typer.echo(f"{i}. {result['name']}")

    choice = int(typer.prompt("Pick a number")) - 1
    if choice >= 0 and choice <= len(results):
        lyrics = fetch_lyrics(results[choice]["url"])

        if output:
            with open(output, "w", encoding="utf-8") as f:
                if lyrics:
                    f.write(lyrics)
                    typer.echo(f"Lyrics written to {output}")
                else:
                    typer.echo(f"Could not find lyrics for {results[choice]['name']}")
                    typer.Exit(code=1)
        else:
            print(lyrics)
    else:
        typer.echo("Invalid choice!")
