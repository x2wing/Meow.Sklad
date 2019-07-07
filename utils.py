from jinja2 import Template

def popup_html_gen(item):
    # try:

    #     # del(item['Координаты'])
    # except:
    #     pass
    goods = {k:v for k, v in item.items() if k !='Координаты'}
    html = """<table border="1">
       <caption>товары</caption>"""

    text = '{% for k, v in item.items() %} <tr><td>{{ k }}</td> <td>{{ v["объём"] }} {{ v["единицы"] }}</td> {% endfor %}'
    template = Template(text)
    html+=template.render(item=goods)


    # print(item)
    html += '</table>'
    return html