from flask import session
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from modules.DatabaseModule.DBManager import DBManager

get_parser = api.parser()


class UserQueryOnlineParticipants(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get online participants uuids.',
             responses={200: 'Success'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        args = get_parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        try:
            accessible_participants = user_access.get_accessible_participants_uuids()

            if not self.test:
                rpc = RedisRPCClient(self.flaskModule.config.redis_config)
                status_participants = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'status_participants')
            else:
                status_participants = {accessible_participants[0]: {'online': True, 'busy': False}}

            participants_uuids = [participant_uuid for participant_uuid in status_participants]
            # Filter participants that are available to the query
            filtered_participants_uuids = list(set(participants_uuids).intersection(accessible_participants))

            # Query participants information
            participants = TeraParticipant.query.filter(TeraParticipant.participant_uuid.in_(
                filtered_participants_uuids)).order_by(TeraParticipant.participant_name.asc()).all()

            participants_json = [participant.to_json(minimal=True) for participant in participants]
            for participant in participants_json:
                participant['participant_online'] = status_participants[participant['participant_uuid']]['online']
                participant['participant_busy'] = status_participants[participant['participant_uuid']]['busy']

            return participants_json

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryOnlineParticipants.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Internal server error when making RPC call.'), 500


