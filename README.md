# satellite6_tools

Library to query and update objects in Satellite 6 such as hosts and content views.

# deep_promoter.py

Recursively promote a composite content view and (a subset of) its component views. In the config file you can define sections to group content views. So if you have a composite view named "jboss_eap" which contains 3 normal views named "jboss", "redhat_base" and "redhat_extras" you can update only the os part using:

  deep_promoter.py jboss_eap os
  
assuming you have in the same directory in promoter.ini:

  [main]
  url = https://satellite6.example.com
  organization = Default_Organization
  
  [os]
  views = redhat_base, redhat_extras
