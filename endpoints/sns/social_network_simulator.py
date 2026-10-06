from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
import random as rd
from datetime import datetime, timezone
import json
from uuid import uuid4
from typing import Literal
sns = APIRouter()

async def generate_actions(n: int, k: int,     event_types: tuple):
    n += rd.randint(-(int(n * 0.1)), int(n * 0.1))
    uuids = [str(uuid4()) for _ in range(k) ]

    generated_events = list()
    for _ in range(n):
        current_event = rd.choice(event_types)
        match current_event:
            case 'LIKE' | 'DISLIKE' | 'COMMENT' | 'VIEW':
                event_object = {
                    'type': current_event,
                    'datetime': datetime.now(timezone.utc).isoformat(),
                    'from': rd.choice(uuids),
                    'to': rd.choice(uuids),
                    'post_id': rd.randint(0,1000)
                }
            case 'DELETE-POST' | 'EDIT-POST' | 'CREATE-POST':
                event_object = {
                    'type': current_event,
                    'datetime': datetime.now(timezone.utc).isoformat(),
                    'target': rd.choice(uuids),
                    'post_id': rd.randint(0,1000)
                }
            case 'LOGIN' | 'CREATE-ACCOUNT' | 'DELETE-ACCOUNT' | 'LOGOUT' | 'UNSUCCESS-LOGIN' | 'EDIT-ACCOUNT':
                event_object = {
                    'type': current_event,
                    'datetime': datetime.now(timezone.utc).isoformat(),
                    'target': rd.choice(uuids)
                }

            case _:
                event_object = {
                    'type': 'UNTYPED-EVENT',
                    'datetime': datetime.now(timezone.utc).isoformat(),
                }

        generated_events.append(event_object)
    return generated_events


@sns.post('/sns/setup/')
async def setup(
        nEventPerRequest: int,
        kTotalUsers: int,
        ):
    if nEventPerRequest > 1000:
        nEventPerRequest = 1000
    
    if kTotalUsers > 500:
        kTotalUsers = 500
    with open('endpoints/sns/social_network_simulator.json', 'w') as f:
        settings = {
            "nEventPerRequest": nEventPerRequest,
            "kTotalUsers": kTotalUsers,
        }
        json.dump(settings, f)
        return JSONResponse({'status': 'ok', 'data': settings})

async def create_events(mod: str) -> list[dict] | None:
    with open('endpoints/sns/social_network_simulator.json', 'r') as f:
        settings = json.load(f)
        event_types = []
        if 'posts' in mod:
            event_types.extend([
                'LIKE', 'CREATE-POST', 'EDIT-POST',
                'DELETE-POST', 'DISLIKE', 'COMMENT', 'VIEW'
                ])
        if 'auth' in mod:
            event_types.extend([
                'LOGIN', 'CREATE-ACCOUNT', 'DELETE-ACCOUNT',
                'LOGOUT', 'UNSUCCESS-LOGIN', 'EDIT-ACCOUNT'
                ])
        if event_types:
            events = await generate_actions(settings.get('nEventPerRequest', 50), settings.get('kTotalUsers', 20), event_types) 
            return events
        return None

def yield_actions(events: list[dict]):
    
    for event in events:
        yield (json.dumps(event) + '\n').encode()
    
@sns.get('/sns/events/actions')
async def json_actions(mod: Literal['posts', 'auth', 'auth+posts']):
        actions = await create_events(mod)
        if actions:
            return JSONResponse(content={'status':'ok', 'data': {'mod': mod, 'events': actions}})
            
        return JSONResponse(
            content= {'status':'bad', 'data': {'message': "Allowed events = 'posts', 'auth', 'auth+posts'"}},
            status_code=400
            )

@sns.get('/sns/events/actions/stream')
async def stream_actions(mod: Literal['posts', 'auth', 'auth+posts']):
    actions = await create_events(mod)
    if actions:
        return StreamingResponse(yield_actions(actions), media_type='application/x-ndjson')
    
    return JSONResponse(
            content= {'status':'bad', 'data': {'message': "Allowed events = 'posts', 'auth', 'auth+posts'"}},
            status_code=400
            )

