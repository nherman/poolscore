import re
import base64
import json
import urllib

from flask import Blueprint, request, render_template, \
            flash, g, redirect, url_for, \
            send_from_directory, jsonify

from sqlalchemy import exc, func, and_

from poolscore import db
from poolscore import app
from poolscore.mod_common.utils import SecurityUtil
from poolscore.mod_common.utils import Util, ModelUtil, ApiError
from poolscore.mod_common.rulesets import Rulesets
from poolscore.mod_common.scoring import Scoring
from poolscore.mod_auth.models import User
from poolscore.mod_play.models import Tourney, Match, MatchPlayer, Game


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
        before_http_action_callback(klass, id, method, attributes, additional_attributes)
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
        before_http_action_callback(klass, id, method, attributes, additional_attributes)
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


@mod_api.before_request
def load_pager(*args, **kwargs):
    g._pager = Util.build_pager(request)

#Ensure that events dict has all required events before serializing
#Assign to before_http_action_callback for POST or PUT request
def update_events_callback(klass=None, id=None, method=None, attributes=None, additional_attributes=None):
    if klass and attributes:
        klass_name = ModelUtil.underscore(klass.__name__)
        klass_attributes = ModelUtil._find_attrs_by_class_name(klass, attributes)
        if klass_attributes and 'events' in klass_attributes:
            ruleset = None

            # get ruleset from attributes or entity
            if (klass_attributes and 'ruleset' in klass_attributes):
                ruleset = klass_attributes["ruleset"]
            elif(additional_attributes and 'ruleset' in additional_attributes):
                ruleset = additional_attributes["ruleset"]
            else:
                entity = klass.secure_query().filter(klass.id == id).first()
                ruleset = entity.ruleset

            if (ruleset != None):
                events = update_events(ruleset, klass_name, klass_attributes)

                #convert events dict to string before writing to DB
                klass_attributes["events"] = json.dumps(events)
                attributes[klass_name] = klass_attributes            

def update_events(ruleset, klass_name, klass_attributes={}):
    if ("events" in klass_attributes):
        # Get default event dict
        events = Rulesets[ruleset][klass_name + "_events"]

        # Update events dict with new values
        for label in klass_attributes["events"]:
            if label in events:
                events[label] = klass_attributes["events"][label]

        return events

# Tourneys
# GET all Tourneys
# GET Tourney by ID
# Update Tourney (PUT)
# Create Tourney (POST)
# Note: _process_request can't handle mircoseconds on dates. Tourney date must be in "%Y%m%dT%H:%M:%S" format
@mod_api.route('/tourneys.json', defaults = {'id': None}, methods = ['GET', 'POST'])
@mod_api.route('/tourneys/<int:id>.json', defaults = {'json_serializer_property': 'serialize_deep'}, methods = ['GET','PUT'])
@SecurityUtil.requires_auth()
def tourneys(id, json_serializer_property=None):
    before_http_action_callback = None
    if request.method == "POST" or request.method == "PUT":
        before_http_action_callback = update_events_callback

    return _process_request(klass = Tourney, 
                            id = id,
                            before_http_action_callback = before_http_action_callback,
                            json_serializer_property = json_serializer_property)

@mod_api.route('/tourneys/count.json', methods = ['GET'])
@SecurityUtil.requires_auth()
def tourneys_count():
    return _process_count_request(klass = Tourney)

# Matches
# GET all Matches for tourney
# GET Match by ID
# Update Match by ID (PUT)
# Create Match for Tourney (POST)
@mod_api.route('/tourneys/<int:tourney_id>/matches.json', defaults = {'match_id': None}, methods = ['GET', 'POST'])
@mod_api.route('/tourneys/<int:tourney_id>/matches/<int:match_id>.json', defaults = {'json_serializer_property': 'serialize_deep'}, methods = ['GET', 'PUT'])
@SecurityUtil.requires_auth()
def match(tourney_id, match_id, json_serializer_property=None):
    tourney = Tourney.secure_query().filter(Tourney.id == tourney_id).first()
    if not tourney:
        raise ApiError("Resource not found for tourney id {}".format(tourney_id), status_code = 404)

    before_http_action_callback = None
    query = None
    additional_attributes = dict(tourney_id = tourney_id)

    #format events properly
    if request.method == "PUT":
        before_http_action_callback = update_events_callback

    if match_id:
        #PUT or GET for a specific Game
        query = Match.secure_query().filter(and_(Match.id == match_id))

    elif request.method == "GET":
        #GET all Matches for Tourney
        query = Match.secure_query().filter(Match.tourney_id == tourney_id).order_by(Match.id)

    elif request.method == "POST":
            ###
            # Create new match for tourney
            #
            # attributes format:
            # {
            #   "match": {
            #       "events": {
            #           match_event: "",
            #           ...
            #      },
            #       match_attribute: "",
            #       ...
            #      "home_players": [],
            #      "away_players": [],
            #   }
            # }
            ###

            attributes = request.get_json(force = True, silent = True, cache = False)
            match_attributes = ModelUtil._find_attrs_by_class_name(Match, attributes)

            # populate match events
            events = update_events(tourney.ruleset, "match", match_attributes)
            match_attributes["events"] = json.dumps(events)
            attributes["match"] = match_attributes            

            try:
                #Create match entity
                match = ModelUtil.create_model(Match, attributes, additional_attributes = additional_attributes)
                if not match:
                    raise ApiError('Match cannot be created. Invalid json format', status_code = 400)

                db.session.add(match)
                db.session.commit()

                match_id = match.id

            except exc.SQLAlchemyError as ex:
                db.session.rollback()
                app.logger.error("Match cannot be created", exc_info = ex)
                raise ApiError('Match cannot be created - [%s]' % ex.message, status_code = 400)


            try:
                #assign players to match
                def assign_players(player_ids, is_home_team):
                    for pid in player_ids:
                        matchplayer = MatchPlayer(
                            match_id = match_id,
                            player_id = pid,
                            is_home_team = is_home_team)
                        db.session.add(matchplayer)

                #Assign Home Player(s)
                assign_players(match_attributes["home_players"], True)

                #Assign Away Player(s)
                assign_players(match_attributes["away_players"], False)
            
                db.session.commit()
            except exc.SQLAlchemyError as ex:
                db.session.rollback()
                app.logger.error("Match Player cannot be created", exc_info = ex)
                raise ApiError('Match Player cannot be created - [%s]' % ex.message, status_code = 400)

            http_resp = jsonify({"match": match.serialize_deep})
            http_resp.status_code = 201
            return http_resp


    return _process_request(klass = Match,
                            id = match_id,
                            query = query,
                            before_http_action_callback = before_http_action_callback,
                            additional_attributes = additional_attributes,
                            json_serializer_property = json_serializer_property)

# Games
# GET all games for match
# GET game by ID
# PUT game update
# POST create new game
@mod_api.route('/tourneys/<int:tourney_id>/matches/<int:match_id>/games.json', defaults = {'game_id': None}, methods = ['GET', 'POST'])
@mod_api.route('/tourneys/<int:tourney_id>/matches/<int:match_id>/games/<int:game_id>.json', methods = ['GET', 'PUT'])
@SecurityUtil.requires_auth()
def game(tourney_id, match_id, game_id):
    match = Match.secure_query().filter(Match.id == match_id).first()
    if not match:
        raise ApiError("Resource not found for match id {}".format(match_id), status_code = 404)

    before_http_action_callback = None
    query = None
    additional_attributes = dict(match_id = match_id)

    #format events properly
    if request.method == "POST" or request.method == "PUT":
        before_http_action_callback = update_events_callback

    if game_id:
        #PUT or GET for a specific Game
        query = Game.secure_query().filter(and_(Game.id == game_id))

    elif request.method == "GET":
        #GET all games for match
        query = Game.secure_query().filter(Game.match_id == match_id).order_by(Game.id)


    return _process_request(klass = Game,
                            id = game_id,
                            query = query,
                            before_http_action_callback = before_http_action_callback,
                            additional_attributes = additional_attributes)

