from tg import MinimalApplicationConfigurator
from setUp.rootController import RootController


# Configure a new minimal application with our root controller.
config = MinimalApplicationConfigurator()
config.update_blueprint({
    'root_controller': RootController(),
    'renderers': ['kajiki', 'json'],
    'kajiki_options': {
        'preferred_doctype': 'html',  # Set your preferred doctype here
    },
    'use_dotted_templatenames': True,
})