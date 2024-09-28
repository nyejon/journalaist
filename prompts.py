def render_template_from_file(prompts_file: str, **kwargs) -> str:

    with open(prompts_file, "r") as file:
        template = file.read()

    result = template.format(**kwargs)

    return result
