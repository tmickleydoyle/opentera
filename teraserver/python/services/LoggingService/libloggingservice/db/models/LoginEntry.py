from services.LoggingService.libloggingservice.db.Base import db
from opentera.db.Base import BaseModel


class LoginEntry(db.Model, BaseModel):
    __tablename__ = "t_logins"
    id_login_event = db.Column(db.Integer, db.Sequence('id_login_event_sequence'), primary_key=True, autoincrement=True)
    login_timestamp = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    login_log_level = db.Column(db.Integer, nullable=False)
    login_sender = db.Column(db.String(), nullable=False)
    login_user_uuid = db.Column(db.String(36), nullable=True)
    login_participant_uuid = db.Column(db.String(36), nullable=True)
    login_device_uuid = db.Column(db.String(36), nullable=True)
    login_service_uuid = db.Column(db.String(36), nullable=True)
    login_status = db.Column(db.Integer, nullable=False)
    login_type = db.Column(db.Integer, nullable=False)
    login_client_ip = db.Column(db.String, nullable=False)
    login_server_endpoint = db.Column(db.String, nullable=True)
    login_client_name = db.Column(db.String, nullable=True)
    login_client_version = db.Column(db.String, nullable=True)
    login_os_name = db.Column(db.String, nullable=True)
    login_os_version = db.Column(db.String, nullable=True)
    login_message = db.Column(db.String, nullable=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        return super().to_json(ignore_fields=ignore_fields)
