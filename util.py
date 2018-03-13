from jinja2 import Environment, PackageLoader, select_autoescape
from database import query
import json

#----------------------------------------------------------------------------
def render(folder, template, **kwargs):
    env = Environment(loader=PackageLoader('main', folder))
    def doQuery(sql, args = {}):
        return query(sql, args)
    
    def tojson(data, **kwargs):
        return json.dumps(data, **kwargs)
    
    env.filters['tojson'] = tojson
    env.globals['doQuery'] = doQuery   
    t = env.get_template(template)
    return t.render(**kwargs)
