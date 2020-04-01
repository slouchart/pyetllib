import click
import functools

from .utlpwd import PasswordReader
from ..context import ExecContext, create_exec_context


def authentication(envvar_prefix=''):
    pwd_reader = PasswordReader(envvar_prefix=envvar_prefix)

    def read_password(ctx, _, value):

        ctx.ensure_object(ExecContext)

        if ctx.params['username'] is None:
            return value

        if value:
            prompt_text = "Password for {0}".format(ctx.params['username'])
            password = click.prompt(prompt_text, hide_input=True, type=str)
        else:
            try:
                password = pwd_reader.read_password_from_env(
                    expected_user=ctx.params['username']
                )
            except (ValueError, RuntimeError):
                password = None

            if password is None:
                try:
                    password = pwd_reader.read_password_from_file(
                        username=ctx.params['username']
                    )
                except (ValueError, RuntimeError):
                    pass
                if password is None:
                    raise click.BadOptionUsage(
                        'password',
                        'No password file could be found.')

        ctx.obj.set_password(password)
        return value

    def read_username(ctx, _, value):
        ctx.ensure_object(ExecContext)
        ctx.obj.set_username(value)
        return value

    opt_user = click.option(
        '-U', '--username',
        metavar='<user>',
        expose_value=True, is_eager=True,
        callback=read_username,
        envvar=pwd_reader.envvars.username,
        help="The name of the user to authenticate"
    )
    opt_pwd = click.option(
        '-W/-w', '--password/--no-password', 'prompt_password',
        default=True,
        callback=read_password, expose_value=True,
        help="Reads the <user> password from a password file "
             "or from standard input"
    )

    def decorator(f):
        return click.pass_context(
            opt_pwd(
                click.pass_context(
                    opt_user(f)
                )
            )
        )
    return decorator


def bare_context_command_callback(func):
    """Decorate a click.command callback such as its only
    parameter in an ExecContext initialized with
    all option and argument values"""
    @functools.wraps(func)
    def inner(ctx, *args, **kwargs):
        context = create_exec_context(**ctx.params)
        if ctx.obj:
            context.update(**ctx.obj)
        return func(context)

    return inner
