"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Snake Shifter."""


if __name__ == "__main__":
    main(prog_name="snake-shifter")  # pragma: no cover
