from jinja2 import Environment, FileSystemLoader

def process_template(template_file) -> str:
    env = Environment(loader=FileSystemLoader('./'))
    template = env.get_template(template_file)
    return template.render()