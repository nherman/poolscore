import re
import base64
import json
import urllib

from flask import Blueprint, request, render_template, \
            flash, g, redirect, url_for, \
            send_from_directory, jsonify

from sqlalchemy import exc, func
'''
from werkzeug.http import parse_content_range_header, parse_options_header
from werkzeug.utils import secure_filename
from sqlalchemy.sql import label
from boto.exception import BotoServerError, JSONResponseError
'''

from poolscore import db
from poolscore import app
from poolscore.mod_common.utils import SecurityUtil
from poolscore.mod_common.utils import Util, ModelUtil, ApiError
from poolscore.mod_common.rulesets import Rulesets
from poolscore.mod_auth.models import User
from poolscore.mod_play.models import Tourney, Match, Game

'''
from grizzly.mod_common.utils import Util, ModelUtil, SecurityUtil, \
            RegexConverter, ApiError, add_app_url_map_converter, VERIFICATION_TOKEN_TYPE
from grizzly.mod_common.lookups import LookupUtil
from grizzly.mod_common.producer import ProducerUtil
from grizzly.mod_common.shorten import UrlShortener
from grizzly.mod_common.passwords.validators import PasswordValidator, ValidationError

from kodiak.services.cloudsearch import CloudSearch
'''


mod_api = Blueprint('api', __name__, url_prefix = '/api/v1.0')

# Overwrite error templates
@mod_api.errorhandler(ApiError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def _void_action_callback(*args, **kwargs):
    pass

def _process_count_request(klass = None, query = None):
    if query:
        count = query.count()
    else:
        count = klass.query.count()
    return jsonify({'count': count})

def _process_request(klass = None, query = None, 
    id = None, method = None, single_fetch = False,
    additional_attributes = None, 
    before_http_action_callback = None, 
    after_http_action_callback = None,
    pre_commit_action_callback = None,
    json_serializer_property = None):
    if not method:
        method = request.method
    if not before_http_action_callback:
        before_http_action_callback = _void_action_callback
    if not pre_commit_action_callback:
        pre_commit_action_callback = _void_action_callback
    if not json_serializer_property:
        json_serializer_property = 'serialize'
    http_resp = None
    callback_kwargs = {}

    def _serialize_json(item):
        return getattr(item, json_serializer_property)

    if method == 'GET':
        before_http_action_callback(klass, id, method)
        if id or single_fetch:
            if query:
                item = query.first()
            else:
                #item = klass.query.filter_by(id = id).first() original code for reference
                item = klass.secure_query().filter(klass.id == id).first()
            if not item:
                raise ApiError('Resource not found for id %s' % id, status_code = 404)
            http_resp = jsonify({ModelUtil.singularize(klass.__tablename__): _serialize_json(item)})
        else:
            if query:
                pagination = Util.paginate_with_pager(klass, query, g._pager, False)
            else:
                pagination = Util.paginate_with_pager(klass, klass.secure_query(), g._pager, False)
            http_resp = jsonify({ModelUtil.pluralize(klass.__tablename__): [
                _serialize_json(item) for item in pagination.items] if pagination else []})
    elif method == 'POST':
        attributes = request.get_json(force = True, silent = True, cache = False)
        if not attributes:
            raise ApiError('Invalid json syntax', status_code = 400)
        before_http_action_callback(klass, id, method, attributes)
        # TODO: IntegrityError: (raised as a result of Query-invoked autoflush; consider 
        # using a session.no_autoflush block if this flush is occurring prematurely) (IntegrityError)
        # Added no_autoflush to avoid issues with child fetching inside of the create_model call.
        with db.session.no_autoflush:
            try:
                item = ModelUtil.create_model(klass, attributes, additional_attributes)
                # Create operation failed. 
                # No item found for request json data. {"invalid": {...}} 
                if not item:
                    raise ApiError('Resource cannot be created. Invalid json format', status_code = 400)
                db.session.add(item)
                pre_commit_action_callback(klass, id, method)
                db.session.commit()
                id = item.id
            except exc.SQLAlchemyError as ex:
                db.session.rollback()
                app.logger.error("Resource cannot be created", exc_info = ex)
                raise ApiError('Resource cannot be created - [%s]' % ex.message, status_code = 400)
            http_resp = jsonify({ModelUtil.singularize(klass.__tablename__): _serialize_json(item)})
            http_resp.status_code = 201
    elif method == 'PUT':
        attributes = request.get_json(force = True, silent = True, cache = False)
        if not attributes:
            raise ApiError('Invalid json syntax', status_code = 400)
        before_http_action_callback(klass, id, method, attributes)
        if query:
            item = query.first()
        else:
            item = klass.query.filter_by(id = id).first()
        if not item:
            raise ApiError('Resource not found for id %s' % id, status_code = 404)
        with db.session.no_autoflush:
            try:
                item = ModelUtil.update_model(item, attributes, additional_attributes)
                # Update operation failed. 
                # No item found for request json data. {"invalid": {...}} 
                if not item:
                    raise ApiError('Resource cannot be updated. Invalid json format', status_code = 400)
                db.session.merge(item)
                pre_commit_action_callback(klass, id, method)
                db.session.commit()
            except exc.SQLAlchemyError as ex:
                db.session.rollback()
                app.logger.error("Resource cannot be updated", exc_info = ex)
                raise ApiError('Resource cannot be updated - [%s]' % ex.message, status_code = 400)
            http_resp = jsonify({ModelUtil.singularize(klass.__tablename__): _serialize_json(item)})
    elif method == 'DELETE':
        before_http_action_callback(klass, id, method)
        # Re-fetch items before running delete query,
        # so we can use them in the post action callback.
        # Note: We don't fetch items when custom query is passed.
        # We assume user is running a bulk delete operation.
        if query:
            delete_query = query
            item = None
        else:
            delete_query = klass.query.filter_by(id = id) 
            item = delete_query.first()
            if not item:
                raise ApiError('Resource not found for id %s' % id, status_code = 404)
        # Preserve params so we can use them in the after_http_action_callback
        callback_kwargs['deleted_item'] = Util.to_serializable_dict(item, klass) if item else None
        with db.session.no_autoflush:
            try:
                count = delete_query.delete()
                pre_commit_action_callback(klass, id, method)
                db.session.commit()
                app.logger.info("Deleted %s records for entity %s" % (count, klass))
            except exc.SQLAlchemyError as ex:
                db.session.rollback()
                app.logger.error("Resource cannot be deleted", exc_info = ex)
                raise ApiError('Resource cannot be deleted - [%s]' % ex.message, status_code = 400)
        http_resp = jsonify({})
    else:
        raise ApiError('Method not allowed', status_code = 405)
    if after_http_action_callback:
        after_http_action_callback(klass, id, method, http_resp, **callback_kwargs)
    if not http_resp:
        raise ApiError('Response object is empty. Unable to continue processing', status_code = 500)
    return http_resp

def _generic_update(entity):
    with db.session.no_autoflush:
        try:
            db.session.merge(entity)
            db.session.commit()
        except exc.SQLAlchemyError as ex:
            db.session.rollback()
            app.logger.error("Resource cannot be updated", exc_info = ex)
            raise ApiError('Resource cannot be updated - [%s]' % ex.message, status_code = 400)
    return entity

@mod_api.before_request
def load_pager(*args, **kwargs):
    g._pager = Util.build_pager(request)


# tourneys
@mod_api.route('/tourneys.json', defaults = {'id': None}, methods = ['GET'])
@mod_api.route('/tourneys/<int:id>.json', defaults = {'serialize': 'serialize_deep'}, methods = ['GET'])
@SecurityUtil.requires_auth()
def tourneys(id, serialize):
    return _process_request(klass = Tourney, id = id, json_serializer_property = serialize)

@mod_api.route('/tourneys/count.json', methods = ['GET'])
@SecurityUtil.requires_auth()
def tourneys_count():
    return _process_count_request(klass = Tourney)

# tourney matches
@mod_api.route('/tourneys/<int:tourney_id>/matches.json', defaults = {'match_id': None}, methods = ['GET', 'POST'])
@mod_api.route('/tourneys/<int:tourney_id>/matches/<int:match_id>.json', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
def match(tourney_id, match_id):
    tourney = Tourney.secure_query().filter(Tourney.id == tourney_id).first()
    if not tourney:
        raise ApiError("Resource not found for tourney id {}".format(tourney_id), status_code = 404)

    additional_attributes = dict(tourney_id = tourney_id)
    query = None

    if match_id:
        query = Match.secure_query().filter(Match.tourney_id == tourney_id and Match.id == match_id)

    else:
        if request.method == "POST":
            attributes = request.get_json(force = True, silent = True, cache = False)
            match_attributes = ModelUtil._find_attrs_by_class_name(Match, attributes)

            try:
                match = ModelUtil.create_model(Match, attributes, additional_attributes = additional_attributes)
                if not match:
                    raise ApiError('Match cannot be created. Invalid json format', status_code = 400)

                events = Rulesets[tourney.ruleset].match_events
                for label in events:
                    if label in attributes:
                        print "LABEL: {}".format(label)
                        events[label] = attributes[label]

                match.events = json.dumps(events)
                db.session.add(match)
                db.session.commit()

            except exc.SQLAlchemyError as ex:
                db.session.rollback()
                app.logger.error("Match cannot be created", exc_info = ex)
                raise ApiError('Match cannot be created - [%s]' % ex.message, status_code = 400)


            def assign_players(player_ids, is_home_team):
                for pid in player_ids:
                    matchplayer = MatchPlayer(
                        match_id = match.id,
                        player_id = pid,
                        is_home_team = is_home_team)
                    db.session.add(matchplayer)

            try:

                print "ATTRIBUTES: {}".format(attributes)

                #Assign Home Player(s)
                assign_players(attributes["home_players"], True)

                #Assign Away Player(s)
                assign_players(attributes["away_players"], False)
            
                db.session.commit()
            except exc.SQLAlchemyError as ex:
                db.session.rollback()
                app.logger.error("Match Player cannot be created", exc_info = ex)
                raise ApiError('Match Player cannot be created - [%s]' % ex.message, status_code = 400)



            http_resp = jsonify({"match": match.serialize_deep})
            http_resp.status_code = 201
            return http_resp

        else:
            query = Match.secure_query().filter(Match.tourney_id == tourney_id)


    return _process_request(klass = Match, id = match_id, query = query, additional_attributes = additional_attributes)


