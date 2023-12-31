from django.urls import path
from .views import *




urlpatterns = {
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('checkUsername/<str:username>/', CheckUsernameView.as_view()),
    path('checkEmail/<str:email>/', CheckEmailView.as_view()),
    path('get_conversation/<int:conversation_id>', GetConversationView.as_view()),
    path('get_conversations', GetConversationsView.as_view()),
    path('delete_conversation/<int:conversation_id>/', DeleteConversationView.as_view()),
    path('send_message/<str:conversation_id>/', SendMessageView.as_view()),
    path('AIresponse/<str:conversation_id>/', GetAIresponseView.as_view()),
}