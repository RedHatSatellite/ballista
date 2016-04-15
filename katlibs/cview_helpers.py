def get_components(datalist, index):
    # Given a list of dictionaries, return the first key encountered in the first dict
    # so given datalist =
    # [{'name': 'name1', 'val1': 'val1'}, {'name': 'name2', 'val': 'val2'}]
    # we can get only the second item:
    # get_components(datalist, ('name', 'name2'))

    search_key = index[0]
    search_val = index[1]

    for structure in datalist:
        try:
            if structure[search_key] == search_val:
                return structure
        except KeyError:
            pass

    return None


def get_latest_version_id(version_list):
    highest_ver = sorted([float(v['version']) for v in version_list])[-1]
    try:
        return get_components(version_list, ('version', unicode(highest_ver)))['id']
    except KeyError:
        pass


def update_and_publish_comp(connection, compview, version_dict):
    # Update and publish the content view with the newest version of
    # the cv's passed in version_dict which looks like
    # { <cv_id>: <version_id> }

    version_list = list()

    for component in compview['components']:
        cv_id = component['content_view_id']
        try:
            version_list.append(version_dict[str(cv_id)])
        except KeyError:
            version_list.append(component['id'])

    connection.update_view(compview['id'], {
        'id': compview['id'],
        'component_ids': version_list,
    })

    connection.publish_view(compview['id'])


def recursive_update(connection, cvs):
    all_views = connection.content_views
    version_dict = dict()
    viewids_to_update = list()
    comps_to_update = list()

    # Get ids of views
    for view in all_views:
        viewids_to_update = viewids_to_update + [c['content_view_id'] for c in view['components'] if
                                                 c['content_view']['name'] in cvs]

    for cvid in viewids_to_update:
        connection.publish_view(cvid, {'id': cvid})

    # Find which composites are impacted
    for view in all_views:
        if view['composite'] and set([i['content_view_id'] for i in view['components']]).intersection(
                viewids_to_update):
            comps_to_update.append(view)

    # Get the ids of the new versions
    for cvid in viewids_to_update:
        versions = get_components(connection.content_views, ('id', cvid))['versions']
        latest_version = get_latest_version_id(versions)
        version_dict[str(cvid)] = latest_version

    for view in comps_to_update:
        update_and_publish_comp(connection, view, version_dict)
