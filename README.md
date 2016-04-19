# satellite6_tools

Library to query and update objects in Satellite 6 such as hosts and content views.

# promote_cv_chain.py

Publish and promote a content view and all composite views that use it. To define the view an ini file is used to group them.  
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

> promote_cv_chain.py os
  
This will publish new versions of the **redhat_base** and **redhat_extras** content views as well as any composite views that containt these. Note that the latter are not promoted, only published.

# State of the code

Please note that while this code is used in semi-production, there is still a lack of things like error-handling and
tests. I expect this will change in the near-future (pull requests welcome!), but as always, use at your own peril:)