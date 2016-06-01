# Ballista

Library to query and update objects in Satellite 6 such as hosts and content views.

# promote_cv_chain.py

Publish and promote a content view and all composite views that use it. To define the view an ini file can be used to group them.
Assuming you have in the same directory in chain_config.ini:

```
[main]
url = https://satellite6.example.com
organization = Default_Organization

[os]
views = redhat_base, redhat_extras

[app]
views = oracle_11g, jboss_eap
```
  
We can promote the os views when we are ready to patch:

> promote_cv_chain.py -c /path/to/config os

Or, if we only want to do oracle_11g:

> promote_cv_chain.py -c /path/to/config oracle_11g
  
This will publish new versions of the **redhat_base** and **redhat_extras** content views as well as any composite views that containt these. Note that the latter are not promoted, only published.

# cleanout_view.py

Remove every unused version from a Content View (versions that have no environments associated).

```
usage: cleanout_view.py [-h] [-c CONF_FILE] [-a] [view_name]

positional arguments:
  view_name             Clean all unused versions in a specific content view
                        (only required if no --all option is given)

optional arguments:
  -h, --help            show this help message and exit
  -c CONF_FILE, --config CONF_FILE
                        Location of the config file
  -a, --all             Clean all unused versions in all content views
```

where the ini file should look like:
```
[main]
url = https://satellite6.example.com
organization = Default_Organization
```

# State of the code

Please note that while this code is used in semi-production, there is still a lack of things like error-handling and
tests. I expect this will change in the near-future (pull requests welcome!), but as always, use at your own peril:)
