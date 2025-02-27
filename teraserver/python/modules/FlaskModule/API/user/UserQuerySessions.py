from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session', type=int, help='ID of the session to query')
get_parser.add_argument('id_participant', type=int, help='ID of the participant from which to get all sessions')
get_parser.add_argument('id_user', type=int, help='ID of the user from which to get all sessions')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to get all sessions')
get_parser.add_argument('status', type=int, help='Limit to specific session status')
get_parser.add_argument('limit', type=int, help='Maximum number of results to return')
get_parser.add_argument('offset', type=int, help='Number of items to ignore in results, offset from 0-index')
get_parser.add_argument('session_uuid', type=str, help='Session UUID to query')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')
get_parser.add_argument('start_date', type=inputs.date, help='Start date, sessions before that date will be ignored')
get_parser.add_argument('end_date', type=inputs.date, help='End date, sessions after that date will be ignored')
get_parser.add_argument('with_session_type', type=inputs.boolean, help='Include session type informations')

post_parser = api.parser()
post_schema = api.schema_model('user_session', {'properties': TeraSession.get_json_schema(),
                                                'type': 'object',
                                                'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Session ID to delete', required=True)


class UserQuerySessions(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get sessions information. Only one of the ID parameter is supported and required at once',
             responses={200: 'Success - returns list of sessions',
                        400: 'No parameters specified at least one id must be used',
                        500: 'Database error'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        sessions = []
        # Can't query sessions, unless we have a parameter!
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        elif args['id_participant']:
            if args['id_participant'] in user_access.get_accessible_participants_ids():
                sessions = TeraSession.get_sessions_for_participant(part_id=args['id_participant'],
                                                                    status=args['status'], limit=args['limit'],
                                                                    offset=args['offset'],
                                                                    start_date=args['start_date'],
                                                                    end_date=args['end_date'])
        elif args['id_session']:
            sessions = [user_access.query_session(args['id_session'])]
        elif args['id_user']:
            if args['id_user'] in user_access.get_accessible_users_ids():
                sessions = TeraSession.get_sessions_for_user(user_id=args['id_user'], status=args['status'],
                                                             limit=args['limit'], offset=args['offset'],
                                                             start_date=args['start_date'], end_date=args['end_date'])
        elif args['id_device']:
            if args['id_device'] in user_access.get_accessible_devices_ids():
                sessions = TeraSession.get_sessions_for_device(device_id=args['id_device'], status=args['status'],
                                                               limit=args['limit'], offset=args['offset'],
                                                               start_date=args['start_date'], end_date=args['end_date'])
        elif args['session_uuid']:
            session_info = TeraSession.get_session_by_uuid(args['session_uuid'])
            if session_info:
                sessions = [user_access.query_session(session_info.id_session)]

        try:
            sessions_list = []
            for ses in sessions:
                if ses is not None:  # Could be none if no access to specified session
                    session_json = ses.to_json(minimal=args['list'])

                    if args['with_session_type']:
                        session_json['session_type_name'] = ses.session_session_type.session_type_name
                        session_json['session_type_color'] = ses.session_session_type.session_type_color

                    sessions_list.append(session_json)

            return jsonify(sessions_list)

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessions.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @api.doc(description='Create / update session. id_session must be set to "0" to create a new '
                         'session. A session can be created/modified if the user has access to all participants and '
                         'users in the session.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified session',
                        400: 'Badly formed JSON or missing fields(session, id_session, session_participants_ids and/or '
                             'session_users_ids[for new sessions]) in the JSON body',
                        500: 'Internal error when saving session'},
             params={'token': 'Secret token'})
    @api.expect(post_schema)
    @user_multi_auth.login_required
    def post(self):
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'session' not in request.json:
            return gettext('Missing session'), 400

        json_session = request.json['session']

        # Validate if we have an id
        if 'id_session' not in json_session:
            return gettext('Missing id_session'), 400

        # User can modify or add a session if they have access to all the participants and users in the session
        session_parts_ids = []
        session_users_ids = []
        session_devices_ids = []
        if json_session['id_session'] == 0:
            # New session - check if we have a participant or users list
            if 'session_participants_ids' not in json_session and 'session_users_ids' not in json_session:
                return gettext('Missing session participants and users'), 400

        else:
            # Query the session to update
            ses_to_update = user_access.query_session(json_session['id_session'])
            if not ses_to_update:
                return gettext('No access to session.'), 403

        if 'session_participants_ids' in json_session:
            session_parts_ids = json_session['session_participants_ids']
            del json_session['session_participants_ids']
        if 'session_users_ids' in json_session:
            session_users_ids = json_session['session_users_ids']
            del json_session['session_users_ids']
        if 'session_devices_ids' in json_session:
            session_devices_ids = json_session['session_devices_ids']
            del json_session['session_devices_ids']

        accessibles_part_ids = user_access.get_accessible_participants_ids()
        if set(session_parts_ids).difference(accessibles_part_ids):
            # At least one participant is not accessible to the user
            return gettext('User doesn\'t have access to at least one participant of that session.'), 403

        accessibles_user_ids = user_access.get_accessible_users_ids()
        if set(session_users_ids).difference(accessibles_user_ids):
            # At least one session user is not accessible to the user
            return gettext('User doesn\'t have access to at least one user of that session.'), 403

        accessibles_device_ids = user_access.get_accessible_devices_ids()
        if set(session_devices_ids).difference(accessibles_device_ids):
            # At least one session user is not accessible to the user
            return gettext('User doesn\'t have access to at least one device of that session.'), 403

        # Do the update!
        if json_session['id_session'] > 0:
            # Already existing
            try:
                TeraSession.update(json_session['id_session'], json_session)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQuerySessions.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_ses = TeraSession()
                new_ses.from_json(json_session)
                TeraSession.insert(new_ses)
                # Update ID for further use
                json_session['id_session'] = new_ses.id_session
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQuerySessions.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_session = TeraSession.get_session_by_id(json_session['id_session'])

        # Manage session participants
        if len(session_parts_ids) > 0:
            update_session.session_participants = [TeraParticipant.get_participant_by_id(part_id)
                                                   for part_id in session_parts_ids]

        # Manage session users
        if len(session_users_ids) > 0:
            update_session.session_users = [TeraUser.get_user_by_id(user_id)
                                            for user_id in session_users_ids]

        # Manage session devices
        if len(session_devices_ids) > 0:
            update_session.session_devices = [TeraDevice.get_device_by_id(device_id)
                                              for device_id in session_devices_ids]

        if session_users_ids or session_parts_ids or session_devices_ids:
            # Commit the changes
            update_session.commit()

        update_session_json = update_session.to_json()
        # Also include session type information
        update_session_json['session_type_name'] = update_session.session_session_type.session_type_name
        update_session_json['session_type_color'] = update_session.session_session_type.session_type_color

        return [update_session.to_json()]

    @api.doc(description='Delete a specific session',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete session (must have access to all participants and users in the '
                             'session to delete)',
                        500: 'Database error.'},
             params={'token': 'Secret token'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        user_access = DBManager.userAccess(current_user)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # User can delete a session if it has access to one of its participant
        todel_session = TeraSession.get_session_by_id(id_todel)
        session_parts_ids = [part.id_participant for part in todel_session.session_participants]
        session_users_ids = [user.id_user for user in todel_session.session_users]
        session_devices_ids = [device.id_device for device in todel_session.session_devices]

        accessibles_part_ids = user_access.get_accessible_participants_ids()
        if set(session_parts_ids).difference(accessibles_part_ids):
            # At least one participant is not accessible to the user
            return gettext('User doesn\'t have access to at least one participant of that session.'), 403

        accessibles_user_ids = user_access.get_accessible_users_ids()
        if set(session_users_ids).difference(accessibles_user_ids):
            # At least one session user is not accessible to the user
            return gettext('User doesn\'t have access to at least one user of that session.'), 403

        accessibles_device_ids = user_access.get_accessible_devices_ids()
        if set(session_devices_ids).difference(accessibles_device_ids):
            # At least one session user is not accessible to the user
            return gettext('User doesn\'t have access to at least one device of that session.'), 403

        from opentera.db.models.TeraSession import TeraSessionStatus
        if todel_session.session_status == TeraSessionStatus.STATUS_INPROGRESS.value:
            return gettext('Session is in progress: can\'t delete that session.'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSession.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessions.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
