from jinja2 import Template

template = Template('Hello {{ name }}!')
print(type(template.render(name=u'Вася')))