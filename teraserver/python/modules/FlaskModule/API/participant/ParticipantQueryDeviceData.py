from flask import jsonify, session, send_file
from flask_restplus import Resource, reqparse, fields, inputs
from modules.LoginModule.LoginModule import participant_multi_auth
from modules.FlaskModule.FlaskModule import participant_api_ns as api
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.DBManagerTeraParticipantAccess import DBManagerTeraParticipantAccess
from libtera.db.DBManager import DBManager
import zipfile
from io import BytesIO
from slugify import slugify

# Parser definition(s)
get_parser = api.parser()
# TODO by id_device_data
get_parser.add_argument('id_device_data', type=int, help='Specific ID of device data to request data.')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all data')
get_parser.add_argument('id_session', type=int, help='ID of session from which to request all data')
get_parser.add_argument('download', type=inputs.boolean, help='If this flag is set, data will be downloaded instead of queried. '
                                                    'In the case there\'s multiple files in the dataset, data will be '
                                                    'zipped before the download process begins', default=False)

post_parser = api.parser()


class ParticipantQueryDeviceData(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @participant_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get device data information. Optionaly download the data.',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):

        current_participant = TeraParticipant.get_participant_by_uuid(session['_user_id'])
        participant_access = DBManager.participantAccess(current_participant)

        args = get_parser.parse_args(strict=True)

        # Storing TeraDeviceData objects.
        device_data_list = []

        # TODO Filter by id_device_data
        if args['id_device']:
            for data in participant_access.query_device_data(args['id_device']):
                if args['id_session']:
                    if data.id_session == args['id_session']:
                        device_data_list.append(data)
                else:
                    device_data_list.append(data)
        else:
            for device in current_participant.participant_devices:
                for data in participant_access.query_device_data(device.id_device):
                    if args['id_session']:
                        if data.id_session == args['id_session']:
                            device_data_list.append(data)
                    else:
                        device_data_list.append(data)

        # Asking for download ?
        if args['download'] is False or len(device_data_list) == 0:
            # Convert to json
            json_list = []
            for data in device_data_list:
                json_list.append(data.to_json())
            return json_list
        else:
            # File transfer requested
            src_dir = self.module.config.server_config['upload_path']

            if len(device_data_list) > 1:
                # More than one file making a zip package...
                zip_ram = BytesIO()
                zfile = zipfile.ZipFile(zip_ram, compression=zipfile.ZIP_DEFLATED, mode='w')

                for data in device_data_list:
                    archive_name = slugify(data.devicedata_session.session_name) + '/' + \
                                   data.devicedata_original_filename
                    zfile.write(src_dir + '/' + str(data.devicedata_uuid), arcname=archive_name)
                zfile.close()
                zip_ram.seek(0)

                file_name = slugify(current_participant.participant_name)

                response = send_file(zip_ram, as_attachment=True, attachment_filename=file_name + '.zip',
                                     mimetype='application/octet-stream')
                response.headers.extend({
                    'Content-Length': zip_ram.getbuffer().nbytes
                })
                return response
            else:
                # Single file
                filename = device_data_list[0].devicedata_original_filename
                return send_file(src_dir + '/' + str(device_data_list[0].devicedata_uuid), as_attachment=True,
                                 attachment_filename=filename)

    @participant_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def post(self):
        return '', 501
