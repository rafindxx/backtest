# Configuration-folder/settings/__init__.py

# Do not forget to add '_development_settings.py' in .gitignore


# Since '_development_settings' is in gitigonre, hence _production_settings
# will be selected for online-server


# select 'development' or 'production' server
try:
    from .dev_settings import *
except:
    from .prod_settings import *