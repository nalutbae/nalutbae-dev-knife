"""
Main CLI entry point for the DevKnife system.
"""

import click


@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    Python DevKnife Toolkit - 개발자를 위한 올인원 터미널 유틸리티 툴킷
    """
    pass


if __name__ == "__main__":
    main()