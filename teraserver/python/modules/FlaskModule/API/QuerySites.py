from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth, db_man
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSiteAccess import TeraSiteAccess


class QuerySites(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id_site', type=int, help='id_site', required=False)
        # self.parser.add_argument('user_uuid', type=str, help='uuid')

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        my_args = {}

        # Make sure we remove the None, safe?
        for key in args:
            if args[key] is not None:
                my_args[key] = args[key]

        try:

            sites = TeraSiteAccess.get_accessible_sites_for_user(current_user)

            sites_list = []
            for site in sites:
                site_json = site.to_json()
                site_json['site_access'] = TeraSiteAccess.get_site_role_for_user(current_user, site)
                sites_list.append(site_json)
            return jsonify(sites_list)
        except InvalidRequestError:
            return '', 500

    def post(self):
        return '', 501

    def delete(self):
        return '', 501
