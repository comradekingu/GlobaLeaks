# -*- encoding: utf-8 -*-
import base64
import os
import shutil

from storm.locals import Int, Bool, Unicode, DateTime, JSON, ReferenceSet

from globaleaks.db.appdata import load_appdata
from globaleaks.db.migrations.update import MigrationBase
from globaleaks.handlers.admin.field import db_import_fields
from globaleaks.handlers.admin.questionnaire import db_get_default_questionnaire_id
from globaleaks.models import Model, BaseModel, Questionnaire, Step, db_forge_obj
from globaleaks.settings import GLSettings


class Node_v_30(Model):
    __storm_table__ = 'node'
    version = Unicode()
    version_db = Unicode()
    name = Unicode()
    public_site = Unicode()
    hidden_service = Unicode()
    receipt_salt = Unicode()
    languages_enabled = JSON()
    default_language = Unicode()
    default_timezone = Int()
    description = JSON()
    presentation = JSON()
    footer = JSON()
    security_awareness_title = JSON()
    security_awareness_text = JSON()
    context_selector_label = JSON()
    maximum_namesize = Int()
    maximum_textsize = Int()
    maximum_filesize = Int()
    tor2web_admin = Bool()
    tor2web_custodian = Bool()
    tor2web_whistleblower = Bool()
    tor2web_receiver = Bool()
    tor2web_unauth = Bool()
    allow_unencrypted = Bool()
    disable_encryption_warnings = Bool()
    allow_iframes_inclusion = Bool()
    submission_minimum_delay = Int()
    submission_maximum_ttl = Int()
    can_postpone_expiration = Bool()
    can_delete_submission = Bool()
    can_grant_permissions = Bool()
    ahmia = Bool()
    wizard_done = Bool()
    disable_submissions = Bool()
    disable_privacy_badge = Bool()
    disable_security_awareness_badge = Bool()
    disable_security_awareness_questions = Bool()
    disable_key_code_hint = Bool()
    disable_donation_panel = Bool()
    enable_captcha = Bool()
    enable_proof_of_work = Bool()
    enable_experimental_features = Bool()
    whistleblowing_question = JSON()
    whistleblowing_button = JSON()
    simplified_login = Bool()
    enable_custom_privacy_badge = Bool()
    custom_privacy_badge_tor = JSON()
    custom_privacy_badge_none = JSON()
    header_title_homepage = JSON()
    header_title_submissionpage = JSON()
    header_title_receiptpage = JSON()
    header_title_tippage = JSON()
    widget_comments_title = JSON()
    widget_messages_title = JSON()
    widget_files_title = JSON()
    landing_page = Unicode()
    show_contexts_in_alphabetical_order = Bool()
    threshold_free_disk_megabytes_high = Int()
    threshold_free_disk_megabytes_medium = Int()
    threshold_free_disk_megabytes_low = Int()
    threshold_free_disk_percentage_high = Int()
    threshold_free_disk_percentage_medium = Int()
    threshold_free_disk_percentage_low = Int()


class User_v_30(Model):
    __storm_table__ = 'user'
    creation_date = DateTime()
    username = Unicode()
    password = Unicode()
    salt = Unicode()
    deletable = Bool()
    name = Unicode()
    description = JSON()
    role = Unicode()
    state = Unicode()
    last_login = DateTime()
    mail_address = Unicode()
    language = Unicode()
    timezone = Int()
    password_change_needed = Bool()
    password_change_date = DateTime()
    pgp_key_info = Unicode()
    pgp_key_fingerprint = Unicode()
    pgp_key_public = Unicode()
    pgp_key_expiration = DateTime()
    pgp_key_status = Unicode()


class Context_v_30(Model):
    __storm_table__ = 'context'
    show_small_cards = Bool()
    show_context = Bool()
    show_recipients_details = Bool()
    allow_recipients_selection = Bool()
    maximum_selectable_receivers = Int()
    select_all_receivers = Bool()
    enable_comments = Bool()
    enable_messages = Bool()
    enable_two_way_comments = Bool()
    enable_two_way_messages = Bool()
    enable_attachments = Bool()
    tip_timetolive = Int()
    name = JSON()
    description = JSON()
    recipients_clarification = JSON()
    status_page_message = JSON()
    show_receivers_in_alphabetical_order = Bool()
    presentation_order = Int()
    questionnaire_id = Unicode()


class ReceiverTip_v_30(Model):
    __storm_table__ = 'receivertip'
    internaltip_id = Unicode()
    receiver_id = Unicode()
    last_access = DateTime()
    access_counter = Int()
    label = Unicode()
    can_access_whistleblower_identity = Bool()
    new = Int()


class Notification_v_30(Model):
    __storm_table__ = 'notification'
    server = Unicode()
    port = Int()
    username = Unicode()
    password = Unicode()
    source_name = Unicode()
    source_email = Unicode()
    security = Unicode()
    admin_pgp_alert_mail_title = JSON()
    admin_pgp_alert_mail_template = JSON()
    admin_anomaly_mail_template = JSON()
    admin_anomaly_mail_title = JSON()
    admin_anomaly_disk_low = JSON()
    admin_anomaly_disk_medium = JSON()
    admin_anomaly_disk_high = JSON()
    admin_anomaly_activities = JSON()
    tip_mail_template = JSON()
    tip_mail_title = JSON()
    file_mail_template = JSON()
    file_mail_title = JSON()
    comment_mail_template = JSON()
    comment_mail_title = JSON()
    message_mail_template = JSON()
    message_mail_title = JSON()
    tip_expiration_mail_template = JSON()
    tip_expiration_mail_title = JSON()
    pgp_alert_mail_title = JSON()
    pgp_alert_mail_template = JSON()
    receiver_notification_limit_reached_mail_template = JSON()
    receiver_notification_limit_reached_mail_title = JSON()
    export_template = JSON()
    export_message_recipient = JSON()
    export_message_whistleblower = JSON()
    identity_access_authorized_mail_template = JSON()
    identity_access_authorized_mail_title = JSON()
    identity_access_denied_mail_template = JSON()
    identity_access_denied_mail_title = JSON()
    identity_access_request_mail_template = JSON()
    identity_access_request_mail_title = JSON()
    identity_provided_mail_template = JSON()
    identity_provided_mail_title = JSON()
    disable_admin_notification_emails = Bool()
    disable_custodian_notification_emails = Bool()
    disable_receiver_notification_emails = Bool()
    send_email_for_every_event = Bool()
    tip_expiration_threshold = Int()
    notification_threshold_per_hour = Int()
    notification_suspension_time=Int()
    exception_email_address = Unicode()
    exception_email_pgp_key_info = Unicode()
    exception_email_pgp_key_fingerprint = Unicode()
    exception_email_pgp_key_public = Unicode()
    exception_email_pgp_key_expiration = DateTime()
    exception_email_pgp_key_status = Unicode()


class MigrationScript(MigrationBase):
    def migrate_Node(self):
        old_node = self.store_old.find(self.model_from['Node']).one()
        new_node = self.model_to['Node']()

        new_templates = [
            'whistleblowing_receipt_prompt'
        ]

        for _, v in new_node._storm_columns.iteritems():
            if self.update_model_with_new_templates(new_node, v.name, new_templates, self.appdata['node']):
                continue

            if v.name == 'allow_indexing':
                new_node.allow_indexing = False
                continue

            if v.name == 'logo_id':
                try:
                    logo_path = os.path.join(GLSettings.static_path, 'logo.png')
                    if not os.path.exists(logo_path):
                        continue

                    new_node.logo =  self.model_to['File']()
                    with open(logo_path, 'r') as logo_file:
                        logo = logo_file.read()
                        new_node.logo.data = base64.b64encode(logo)

                    os.remove(logo_path)

                except:
                    pass

                continue

            if v.name == 'css_id':
                try:
                    css_path = os.path.join(GLSettings.static_path, 'custom_stylesheet.css')
                    if not os.path.exists(css_path):
                        continue

                    new_node.css =  self.model_to['File']()
                    with open(css_path, 'r') as css_file:
                        css = css_file.read()
                        new_node.css.data = base64.b64encode(css)

                    os.remove(css_path)

                except:
                    pass

                continue

            if v.name == 'basic_auth':
                new_node.basic_auth = False
                continue

            if v.name == 'basic_auth_username':
                new_node.basic_auth_username = u''
                continue

            if v.name == 'basic_auth_password':
                new_node.basic_auth_password = u''
                continue

            if v.name == 'contexts_clarification':
                new_node.contexts_clarification = old_node.context_selector_label
                continue

            if v.name == 'context_selector_type':
                new_node.context_selector_type = u'list'
                continue

            if v.name == 'show_small_context_cards':
                new_node.show_small_context_cards = False
                continue

            setattr(new_node, v.name, getattr(old_node, v.name))

        self.store_new.add(new_node)

        try:
            os.remove(os.path.join(GLSettings.static_path, 'default-profile-picture.png'))
        except:
            pass

        try:
            os.remove(os.path.join(GLSettings.static_path, 'robots.txt'))
        except:
            pass

    def migrate_User(self):
        old_objs = self.store_old.find(self.model_from['User'])
        for old_obj in old_objs:
            new_obj = self.model_to['User']()
            for _, v in new_obj._storm_columns.iteritems():
                if v.name == 'img_id':
                    try:
                        img_path = os.path.join(GLSettings.static_path, old_obj.id + ".png")
                        if not os.path.exists(img_path):
                            continue

                        new_obj.picture =  self.model_to['File']()
                        with open(img_path, 'r') as img_file:
                            img = img_file.read()
                            new_obj.picture.data = base64.b64encode(img)

                        os.remove(img_path)

                    except:
                        pass

                    continue

                setattr(new_obj, v.name, getattr(old_obj, v.name))

            self.store_new.add(new_obj)

    def migrate_Context(self):
        old_objs = self.store_old.find(self.model_from['Context'])
        for old_obj in old_objs:
            new_obj = self.model_to['Context']()
            for _, v in new_obj._storm_columns.iteritems():
                if v.name == 'img_id':
                    continue

                if v.name == 'show_small_receiver_cards':
                    new_obj.show_small_receiver_cards = old_obj.show_small_cards
                    continue

                setattr(new_obj, v.name, getattr(old_obj, v.name))

            self.store_new.add(new_obj)


    def migrate_ReceiverTip(self):
        old_objs = self.store_old.find(self.model_from['ReceiverTip'])
        for old_obj in old_objs:
            new_obj = self.model_to['ReceiverTip']()
            for _, v in new_obj._storm_columns.iteritems():
                if v.name == 'enable_notifications':
                    new_obj.enable_notifications = True
                    continue

                setattr(new_obj, v.name, getattr(old_obj, v.name))

            self.store_new.add(new_obj)

    def migrate_Notification(self):
        # TODO an other time fix templates by reloading updated translations TODO
        old_notification = self.store_old.find(self.model_from['Notification']).one()
        new_notification = self.model_to['Notification']()

        for _, v in new_notification._storm_columns.iteritems():
            if self.update_model_with_new_templates(new_notification,
                                                    v.name,
                                                    self.appdata['templates'].keys(),
                                                    self.appdata['templates']):
                continue

        self.store_new.add(new_notification)

    def migrate_Field(self):
        old_objs = self.store_old.find(self.model_from['Field'])
        for old_obj in old_objs:
            new_obj = self.model_to['Field']()
            for _, v in new_obj._storm_columns.iteritems():
                if v.name == 'type':
                    # specific field tpyes email and number have been removed
                    # and the current implementation makes use of inputboxes
                    if old_obj.type in [ 'email', 'number']:
                        new_obj.type = 'inputbox'
                    continue

                setattr(new_obj, v.name, getattr(old_obj, v.name))

            self.store_new.add(new_obj)
