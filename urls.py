from views.chat import (
    List as ChatList,
    Create as ChatCreate,
    Login as ChatLogin,
    Logout as ChatLogout,
    History as ChatHistory,
    Post as ChatPost,
    Websocket as ChatWebsocket,
)
from views.user import Auth as UserAuth

urls = (
    ('*', '/auth', UserAuth),
    ('*', '/chat/list', ChatList),
    ('*', '/chat/create', ChatCreate),
    ('*', '/chat/{id}/login', ChatLogin),
    ('*', '/chat/{id}/logout', ChatLogout),
    ('*', '/chat/{id}/history', ChatHistory),
    ('*', '/chat/{id}/post', ChatPost),
    ('*', '/ws', ChatWebsocket),
)
