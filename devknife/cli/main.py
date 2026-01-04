"""
Main CLI entry point for the DevKnife system.
"""

import sys
import click
from devknife.core import InputData, InputSource
from devknife.core.router import get_global_registry, get_global_router
from devknife.utils.encoding_utility import Base64EncoderDecoder, URLEncoderDecoder


def setup_utilities():
    """Register all available utilities."""
    registry = get_global_registry()
    
    # Register encoding utilities
    registry.register_utility(Base64EncoderDecoder)
    registry.register_utility(URLEncoderDecoder)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    Python DevKnife Toolkit - 개발자를 위한 올인원 터미널 유틸리티 툴킷
    """
    setup_utilities()


@main.command()
@click.argument('text', required=False)
@click.option('--decode', is_flag=True, help='Base64 문자열을 디코딩합니다')
@click.option('--file', '-f', type=click.Path(exists=True), help='파일에서 입력을 읽습니다')
def base64(text, decode, file):
    """Base64 인코딩/디코딩을 수행합니다."""
    router = get_global_router()
    
    # 입력 데이터 준비
    if file:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        input_data = InputData(content=content, source=InputSource.FILE)
    elif text:
        input_data = InputData(content=text, source=InputSource.ARGS)
    elif not sys.stdin.isatty():
        # stdin에서 읽기
        content = sys.stdin.read().strip()
        input_data = InputData(content=content, source=InputSource.STDIN)
    else:
        click.echo("오류: 입력 텍스트가 필요합니다. --help를 참조하세요.")
        return
    
    # 명령 실행
    options = {'decode': decode}
    result = router.route_command('base64', input_data, options)
    
    if result.success:
        click.echo(result.output)
    else:
        click.echo(f"오류: {result.error_message}", err=True)


@main.command()
@click.argument('text', required=False)
@click.option('--decode', is_flag=True, help='URL 인코딩된 문자열을 디코딩합니다')
@click.option('--file', '-f', type=click.Path(exists=True), help='파일에서 입력을 읽습니다')
def url(text, decode, file):
    """URL 인코딩/디코딩을 수행합니다."""
    router = get_global_router()
    
    # 입력 데이터 준비
    if file:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        input_data = InputData(content=content, source=InputSource.FILE)
    elif text:
        input_data = InputData(content=text, source=InputSource.ARGS)
    elif not sys.stdin.isatty():
        # stdin에서 읽기
        content = sys.stdin.read().strip()
        input_data = InputData(content=content, source=InputSource.STDIN)
    else:
        click.echo("오류: 입력 텍스트가 필요합니다. --help를 참조하세요.")
        return
    
    # 명령 실행
    options = {'decode': decode}
    result = router.route_command('url', input_data, options)
    
    if result.success:
        click.echo(result.output)
    else:
        click.echo(f"오류: {result.error_message}", err=True)


@main.command()
def list_commands():
    """사용 가능한 모든 명령어를 나열합니다."""
    registry = get_global_registry()
    router = get_global_router()
    
    click.echo(router.get_general_help())


if __name__ == "__main__":
    main()